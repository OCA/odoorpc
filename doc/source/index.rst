.. OdooRPC documentation master file, created by
   sphinx-quickstart on Sun Jul  6 16:32:50 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OdooRPC's documentation!
===================================

Introduction
------------

**OdooRPC** is a Python module providing an easy way to
pilot your `Odoo <https://www.odoo.com>`_ servers through `RPC`.

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

Quick start
-----------

How does it work? See below::

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

For more details and features, see the :ref:`tutorials <tutorials>`, the
:ref:`Frequently Asked Questions (FAQ) <faq>` and the
:ref:`API reference <reference>` sections.

Contents
--------

.. toctree::
    :maxdepth: 3

    download_install
    tutorials
    faq
    reference

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

Bugs or suggestions
-------------------

Please, feel free to report bugs or suggestions in the `Bug Tracker
<https://github.com/osiell/odoorpc/issues>`_!

Make a donation
---------------

`OdooRPC` is mainly developed on free time. To show your appreciation and
support this project, it is possible to make a donation through `PayPal`:

.. raw:: html

    <div style="padding-left: 5em; text-align: left;">
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
            <input type="hidden" name="cmd" value="_s-xclick">
            <input type="hidden" name="hosted_button_id" value="RCVMUNS5LK5K6">
            <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
            <img alt="" border="0" src="https://www.paypalobjects.com/fr_FR/i/scr/pixel.gif" width="1" height="1">
        </form>
    </div>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

