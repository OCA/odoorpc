#!/bin/sh
# Run tests locally with Python 3 against the official Odoo Docker image.
# Run all tests:
#
#   $ ./run_tests_docker.sh
#
# Run tests partially:
#
#   $ ./run_tests_docker.sh odoorpc.tests.test_env
#
# Docker containers are removed only when running tests globally, this way
# you can run tests partially several times without time penalty:
#
# Depends on:
#   - docker.io
#   - python3-venv
# Optional environment variables:
#   - ORPC_TEST_VERSION=12.0
#   - ORPC_TEST_PORT=8069
#   - ORPC_TEST_DB
#
HERE=$(dirname $(readlink -m $0))
VENV=$HERE/venv_test
[ -z ${ORPC_TEST_VERSION+x} ] && export ORPC_TEST_VERSION="12.0"
[ -z ${ORPC_TEST_PORT+x} ] && export ORPC_TEST_PORT=8069

# Pull images
PG_IMAGE="postgres:9.4"
if [ "$(echo $ORPC_TEST_VERSION'>='12.0 | bc -l)" -eq 1 ]; then
    PG_IMAGE="postgres:10"
fi
PG_CT=pg_odoorpc_test_${ORPC_TEST_VERSION}
ODOO_IMAGE="odoo:$ORPC_TEST_VERSION"
ODOO_CT=odoo_odoorpc_test_${ORPC_TEST_VERSION}
printf "Using Docker images$ODOO_IMAGE + $PG_IMAGE ...\n"
docker pull $PG_IMAGE
docker pull $ODOO_IMAGE

# Run containers
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name $PG_CT $PG_IMAGE
docker run -d -p $ORPC_TEST_PORT:8069 --name $ODOO_CT --link $PG_CT:db -t $ODOO_IMAGE
docker cp $HERE/travis/docker_odoo_fix.sh $ODOO_CT:/docker_odoo_fix.sh
docker exec -it -u root $ODOO_CT sh /docker_odoo_fix.sh

# Install OdooRPC in a Python 3 environment
python3 -m venv $VENV
$VENV/bin/pip install -e $HERE
$VENV/bin/pip install sphinx

# Run tests against the Odoo container
printf "Running tests...\n"
if [ -z ${1+x} ]; then
    # Clean up
    $VENV/bin/python3 -m unittest discover -v
    $VENV/bin/sphinx-build -b doctest -d doc/build/doctrees doc/source build/doctest
else
    $VENV/bin/python3 -m unittest $1 -v
fi
printf "Removing containers...\n"
docker rm -f $ODOO_CT $PG_CT
