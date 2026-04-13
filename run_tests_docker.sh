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
#   - docker.io + docker-compose
#   - python3-venv
#
# Optional environment variables:
#   - ORPC_TEST_VERSION=16.0
#
HERE=$(dirname $(readlink -m $0))
VENV=$HERE/venv_test
[ -z ${ORPC_TEST_VERSION+x} ] && export ORPC_TEST_VERSION="16.0"
[ -z ${ORPC_TEST_PORT+x} ] && export ORPC_TEST_PORT=8069

# Start Odoo
printf "Starting Odoo ${ORPC_TEST_VERSION}...\n"
docker compose -f "$HERE/.ci/odoo-${ORPC_TEST_VERSION}.yml" up -d && sleep 5

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
printf "Stopping Odoo ${ORPC_TEST_VERSION}...\n"
docker compose -f "$HERE/.ci/odoo-${ORPC_TEST_VERSION}.yml" down -v
