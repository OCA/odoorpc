.. _download-install:

Download and install instructions
=================================

Python Package Index (PyPI)
---------------------------

You can install `OdooRPC` with `pip`::

    $ pip install odoorpc

No dependency is required.

Source code
-----------

The project is hosted on `GitHub <https://github.com/osiell/odoorpc>`_.
To get the current development branch (``master``), just type::

    $ git clone https://github.com/osiell/odoorpc.git

For the last version of a stable branch (replace `X.Y` accordingly)::

    $ git checkout X.Y

Run tests
---------

Unit tests depend on the standard module `unittest` (Python 2.7 and 3.x).
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
    $ export ORPC_TEST_VERSION=10.0
    $ export ORPC_TEST_SUPER_PWD=admin
    $ python -m unittest discover -v

The database ``odoorpc_test`` will be created if it does not exist.
