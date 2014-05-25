
=======
OERPLib
=======

**OERPLib** is a Python module providing an easy way to
pilot your **OpenERP** and **Odoo** servers through `RPC`.

Features supported:
    - `XML-RPC` and (legacy) `Net-RPC` protocols,
    - access to all methods proposed by a model class
      (even ``browse``) with an API similar to the server-side API,
    - ability to use named parameters with such methods (server >= `6.1`),
    - user context automatically sent (server >= `6.1`) providing support
      for internationalization,
    - browse records,
    - execute workflows,
    - manage databases,
    - reports downloading,
    - inspection capabilities (graphical output of relations between models and
      dependencies between modules, list ``on_change`` methods from model
      views, ...).

How does it work? See below::

    import oerplib

    # Prepare the connection to the server
    oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)

    # Check available databases
    print(oerp.db.list())

    # Login (the object returned is a browsable record)
    user = oerp.login('user', 'passwd', 'db_name')
    print(user.name)            # name of the user connected
    print(user.company_id.name) # the name of its company

    # Simple 'raw' query
    user_data = oerp.execute('res.users', 'read', [user.id])
    print(user_data)

    # Use all methods of an OSV class
    order_obj = oerp.get('sale.order')
    order_ids = order_obj.search([])
    for order in order_obj.browse(order_ids):
        print(order.name)
        products = [line.product_id.name for line in order.order_line]
        print(products)

    # Update data through a browsable record
    user.name = "Brian Jones"
    oerp.write_record(user)

See the documentation for more details and features.

Supported OpenERP/Odoo server versions
--------------------------------------

`OERPLib` has been tested on `OpenERP` server v5.0, v6.0, v6.1, v7.0 and
Odoo v8.0.
It should work on next versions if `Odoo` keeps a stable API.

Supported Python versions
-------------------------

`OERPLib` support Python versions 2.6, 2.7.

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
<https://bugs.launchpad.net/oerplib>`_!

Changes in this version
-----------------------

Consult the ``CHANGES.txt`` file.

