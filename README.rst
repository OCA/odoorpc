OdooRPC
=======

.. image:: https://img.shields.io/pypi/v/OdooRPC.svg
    :target: https://pypi.python.org/pypi/OdooRPC/
    :alt: Latest Version

.. image:: https://travis-ci.org/osiell/odoorpc.svg?branch=master
    :target: https://travis-ci.org/osiell/odoorpc
    :alt: Build Status

.. image:: https://img.shields.io/pypi/pyversions/OdooRPC.svg
    :target: https://pypi.python.org/pypi/OdooRPC/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/OdooRPC.svg
    :target: https://pypi.python.org/pypi/OdooRPC/
    :alt: License

**OdooRPC** is a Python module providing an easy way to
pilot your **Odoo** servers through `RPC`.

Features supported:
    - access to all data model methods (even ``browse``) with an API similar
      to the server-side API,
    - use named parameters with model methods,
    - user context automatically sent providing support for
      internationalization,
    - browse records,
    - execute workflows,
    - manage databases,
    - reports downloading,
    - JSON-RPC protocol (SSL supported),

How does it work? See below:

.. code-block:: python

    import odoorpc

    # Prepare the connection to the server
    odoo = odoorpc.ODOO('localhost', port=8069)

    # Check available databases
    print(odoo.db.list())

    # Login
    odoo.login('db_name', 'user', 'passwd')

    # Current user
    user = odoo.env.user
    print(user.name)            # name of the user connected
    print(user.company_id.name) # the name of its company

    # Simple 'raw' query
    user_data = odoo.execute('res.users', 'read', [user.id])
    print(user_data)

    # Use all methods of a model
    if 'sale.order' in odoo.env:
        Order = odoo.env['sale.order']
        order_ids = Order.search([])
        for order in Order.browse(order_ids):
            print(order.name)
            products = [line.product_id.name for line in order.order_line]
            print(products)

    # Update data through a record
    user.name = "Brian Jones"

See the documentation for more details and features.

Supported Odoo server versions
------------------------------

`OdooRPC` has been tested on `Odoo` 8.0, 9.0 and 10.0.
It should work on next versions if `Odoo` keeps a stable API.

Supported Python versions
-------------------------

`OdooRPC` support Python 2.7, 3.2, 3.3, 3.4, 3.5 and 3.6.

License
-------

This software is made available under the `LGPL v3` license.

Generate the documentation
--------------------------

To generate the documentation, you have to install `Sphinx` documentation
generator::

    pip install sphinx

Then, you can use the ``build_doc`` option of the ``setup.py``::

    python setup.py build_doc

The generated documentation will be in the ``./doc/build/html`` directory.

Bugs or suggestions
-------------------

Please, feel free to report bugs or suggestions in the `Bug Tracker
<https://github.com/osiell/odoorpc/issues>`_!

Changes in this version
-----------------------

Consult the ``CHANGELOG`` file.
