=======
OdooRPC
=======

**OdooRPC** is a Python module providing an easy way to
pilot your **Odoo** servers through `RPC`.

Features supported:
    - `XML-RPC` and `JSON-RPC` protocols,
    - access to all methods proposed by a model class
      (even ``browse``) with an API similar to the server-side API,
    - use named parameters with model methods,
    - user context automatically sent providing support for
      internationalization,
    - browse records,
    - execute workflows,
    - manage databases,
    - reports downloading.

How does it work? See below::

    import odoorpc

    # Prepare the connection to the server
    odoo = odoorpc.XMLRPC('localhost', port=8069)   # JSONRPC available too

    # Check available databases
    print(odoo.db.list())

    # Login (the object returned is a browsable record)
    user = odoo.login('user', 'passwd', 'db_name')
    print(user.name)            # name of the user connected
    print(user.company_id.name) # the name of its company

    # Simple 'raw' query
    user_data = odoo.execute('res.users', 'read', [user.id])
    print(user_data)

    # Use all methods of a model
    order_model = odoo.registry['sale.order']
    order_ids = order_model.search([])
    for order in order_model.browse(order_ids):
        print(order.name)
        products = [line.product_id.name for line in order.order_line]
        print(products)

    # Update data through a browsable record
    user.name = "Brian Jones"
    odoo.save()

See the documentation for more details and features.

Supported Odoo server versions
------------------------------

`OdooRPC` has been tested on `Odoo` server v8.0.
It should work on next versions if `Odoo` keeps a stable API.

Supported Python versions
-------------------------

`OdooRPC` support Python versions 2.7, 3.2, 3.3 and 3.4

License
-------

This software is made available under the `LGPL v3` license.

Generate the documentation
--------------------------

To generate the documentation, you have to install `Sphinx` documentation
generator::

    easy_install -U sphinx

Then, you can use the ``build_doc`` option of the ``setup.py``::

    python setup.py build_doc

The generated documentation will be in the ``./doc/build/html`` directory.

Bugs or suggestions
-------------------

Please, feel free to report bugs or suggestions in the `Bug Tracker
<TODO>`_!

Changes in this version
-----------------------

Consult the ``CHANGELOG`` file.
