.. _download-install:

Download and install instructions
=================================

Python Package Index (PyPI)
---------------------------

You can install OERPLib with the `easy_install` tool::

    $ easy_install oerplib

Or with `pip`::

    $ pip install oerplib

An alternative way is to download the tarball from
`Python Package Index <http://pypi.python.org/pypi/OERPLib/>`_ page,
and install manually (replace `X.Y.Z` accordingly)::

    $ wget http://pypi.python.org/packages/source/O/OERPLib/OERPLib-X.Y.Z.tar.gz
    $ tar xzvf OERPLib-X.Y.Z.tar.gz
    $ cd OERPLib-X.Y.Z
    $ python setup.py install

No dependency is required except `pydot <http://code.google.com/p/pydot/>`_ for
some methods of the :class:`inspect <oerplib.service.inspect.Inspect>` service
(optional).

Source code
-----------

The project is hosted on `Launchpad <https://launchpad.net/oerplib>`_.
To get the current development branch (the ``trunk``), just type::

    $ bzr branch lp:oerplib

For the last version of a stable branch (replace `X.Y` accordingly)::

    $ bzr branch lp:oerplib/X.Y

Run tests
---------

.. versionadded:: 0.4.0

Unit tests depends on `unittest2` (Python 2.3+) or `unittest`
(Python 2.7 and 3.x), and `argparse`.

To run unit tests from the project directory, run the following command::

    $ PYTHONPATH=.:$PYTHONPATH ./tests/runtests.py --help

Then, set your parameters in order to indicate the `OpenERP` server on which
you want to perform the tests, for instance::

    $ PYTHONPATH=.:$PYTHONPATH ./tests/runtests.py --create_db --server 192.168.1.4 --test_xmlrpc --xmlrpc_port 8069

The name of the database created is ``oerplib-test`` by default.

