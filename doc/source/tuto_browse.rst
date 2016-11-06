.. _tuto-browse-records:

Browse records
**************

A great functionality of `OdooRPC` is its ability to generate objects that are
similar to records used on the server side.

Get records
===========

To get one or more records (a recordset), you will use the
:func:`browse <odoorpc.models.Model.browse>` method from a model proxy::

    >>> Partner = odoo.env['res.partner']
    >>> partner = Partner.browse(1)     # fetch one record, partner ID = 1
    >>> partner
    Recordset('res.partner', [1])
    >>> partner.name
    'YourCompany'
    >>> for partner in Partner.browse([1, 3]):  # fetch several records
    >>>     print(partner.name)
    ...
    YourCompany
    Administrator


From such objects, it is possible to easily explore relationships. The related
records are generated on the fly::

    >>> partner = Partner.browse(1)
    >>> for child in partner.child_ids:
    ...     print("%s (%s)" % (child.name, child.parent_id.name))
    ...
    Mark Davis (YourCompany)
    Roger Scott (YourCompany)

Outside relation fields, `Python` data types are used, like ``datetime.date``
and ``datetime.datetime``::

    >>> Purchase = odoo.env['purchase.order']
    >>> order = Purchase.browse(1)
    >>> order.date_order
    datetime.datetime(2016, 11, 6, 11, 23, 10)

A list of data types used by records fields are available :ref:`here <fields>`.

Get records corresponding to an External ID
===========================================

To get a record through its external ID, use the
:func:`ref <odoorpc.env.Environment.ref>` method from the environment::

    >>> lang_en = odoo.env.ref('base.lang_en')
    >>> lang_en
    Recordset('res.lang', [1])
    >>> lang_en.code
    'en_US'

:ref:`Next step: Call methods from a Model or from records <tuto-browse-methods>`
