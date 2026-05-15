.. OdooRPC documentation master file, created by
   sphinx-quickstart on Sun Jul  6 16:32:50 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OdooRPC's documentation!
===================================

Introduction
------------

**OdooRPC** is a Python package providing an easy way to
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

`OdooRPC` is tested on all major releases of `Odoo` (starting from  8.0).

Supported Python versions
-------------------------

`OdooRPC` support Python 2.7, 3.7+.

License
-------

This software is made available under the `LGPL v3` license.

Bug Tracker
-----------

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/odoorpc/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
-------

Contributors
____________

* Sébastien Alix <sebastien.alix@osiell.com>

Do not contact contributors directly about support or help with technical issues.

Maintainer
__________

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This package is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
