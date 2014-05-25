.. OERPLib documentation master file, created by
   sphinx-quickstart on Thu Sep 15 10:49:22 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OERPLib's documentation!
===================================

Introduction
------------

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

Quick start
-----------

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

    # Use all methods of a model class
    order_obj = oerp.get('sale.order')
    order_ids = order_obj.search([])
    for order in order_obj.browse(order_ids):
        print(order.name)
        products = [line.product_id.name for line in order.order_line]
        print(products)

    # Update data through a browsable record
    user.name = "Brian Jones"
    oerp.write_record(user)

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

Supported OpenERP/Odoo server versions
--------------------------------------

`OERPLib` has been tested on `OpenERP` server v5.0, v6.0, v6.1, v7.0 and
`Odoo` v8.0.
It should work on next versions if `Odoo` keeps a stable API.

Supported Python versions
-------------------------

`OERPLib` support Python versions 2.6, 2.7.

License
-------

This software is made available under the `LGPL v3` license.

Bugs or suggestions
-------------------

Please, feel free to report bugs or suggestions in the `Bug Tracker
<https://bugs.launchpad.net/oerplib>`_!

Make a donation
---------------

`OERPLib` is mainly developed on free time. To show your appreciation and
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

