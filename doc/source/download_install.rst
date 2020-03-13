.. _download-install:

Download and install instructions
=================================

Install from PyPI
-----------------

You can install `OdooRPC` with `pip`::

    $ pip install odoorpc

Install from GitHub
-------------------

To install the latest development branch with `pip`::

    $ pip install git+https://github.com/OCA/odoorpc.git@master

Install from sources
--------------------

The project is hosted on `GitHub <https://github.com/OCA/odoorpc>`_.
To get the last development sources (``master`` branch), just type::

    $ git clone https://github.com/OCA/odoorpc.git
    $ cd odoorpc/ && python setup.py install

Contribute
----------

The project uses `pre-commit` to check the code. To make your life easier you
are encouraged to install `pre-commit`::

    $ pip install pre-commit

And initialize it at the root of the project source tree::

    $ cd ./odoorpc/ && pre-commit install

`pre-commit` will now check your changes when commiting and abort the operation
if the code is not in a good health.

Run tests
---------

Unit tests depend on the standard module `unittest` (Python 2.7 and 3.x) and
on a running Odoo instance.
To run all unit tests from the project directory, run the following command::

    $ python -m unittest discover -v

To run a specific test::

    $ python -m unittest -v odoorpc.tests.test_init

To configure the connection to the server, some environment variables are
available::

    $ export ORPC_TEST_PROTOCOL=jsonrpc
    $ export ORPC_TEST_HOST=localhost
    $ export ORPC_TEST_PORT=8069
    $ export ORPC_TEST_DB=odoorpc_test
    $ export ORPC_TEST_USER=admin
    $ export ORPC_TEST_PWD=admin
    $ export ORPC_TEST_VERSION=12.0
    $ export ORPC_TEST_SUPER_PWD=admin
    $ python -m unittest discover -v

The database ``odoorpc_test`` will be created if it does not exist.

If you have `Docker` installed, an handy script will help you to run the tests
on a dockerized Odoo instance::

    $ ./run_tests_docker.sh

The same environment variables described above apply::

    $ ORPC_TEST_VERSION=11.0 ./run_tests_docker.sh
