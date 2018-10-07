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
#   - ORPC_TEST_VERSION=11.0
#   - ORPC_TEST_PORT=8069
#   - ORPC_TEST_DB
#   - ORPC_TEST_USER
#   - ORPC_TEST_PWD
#   - ORPC_TEST_SUPER_PWD
#
HERE=$(dirname $(readlink -m $0))
VENV=$HERE/venv_test
if [ -z ${ORPC_TEST_VERSION+x} ]; then
    ORPC_TEST_VERSION="12.0"
fi
if [ -z ${ORPC_TEST_PORT+x} ]; then
    ORPC_TEST_PORT=8069
fi
echo $ORPC_TEST_PORT
# Pull images
PG_IMAGE="postgres:9.4"
PG_CT=pg_odoorpc_test_${ORPC_TEST_VERSION}
ODOO_IMAGE="odoo:$ORPC_TEST_VERSION"
ODOO_CT=odoo_odoorpc_test_${ORPC_TEST_VERSION}
docker pull $PG_IMAGE
docker pull $ODOO_IMAGE
# Run containers
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo --name $PG_CT $PG_IMAGE
docker run -d -p $ORPC_TEST_PORT:8069 --name $ODOO_CT --link $PG_CT:db -t $ODOO_IMAGE
# Install OdooRPC in a Python 3 environment
python3 -m venv $VENV
$VENV/bin/pip install -e $HERE
# Run tests against the Odoo container
printf "Running tests...\n"
if [ -z ${1+x} ]; then
    # Clean up
    printf "Removing containers...\n"
    $VENV/bin/python3 -m unittest discover -v
else
    $VENV/bin/python3 -m unittest $1 -v
fi
docker rm -f $ODOO_CT $PG_CT
