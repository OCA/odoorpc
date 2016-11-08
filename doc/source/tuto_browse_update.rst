.. _tuto-update-browse-records:

Update data through records
***************************

By default when updating values of a record, the change is automatically sent
to the server.
Let's update the name of a partner::

    >>> Partner = odoo.env['res.partner']
    >>> partner_id = Partner.create({'name': "Contact Test"})
    >>> partner = Partner.browse(partner_id)
    >>> partner.name = "MyContact"

This is equivalent to::

    >>> Partner.write([partner.id], {'name': "MyContact"})

As one update is equivalent to one RPC query, if you need to update several
fields for one record it is encouraged to use the `write` method as above ::

    >>> partner.write({'name': "MyContact", 'website': 'http://example.net'})    # one RPC query

Or, deactivate the ``auto_commit`` option and commit the changes manually::

    >>> odoo.config['auto_commit'] = False
    >>> partner.name = "MyContact"
    >>> partner.website = 'http://example.net'
    >>> partner.env.commit()    # one RPC by record modified

Char, Float, Integer, Boolean, Text and Binary
''''''''''''''''''''''''''''''''''''''''''''''

As see above, it's as simple as that::

    >>> partner.name = "New Name"

Selection
'''''''''

Same as above, except there is a check about the value assigned. For instance,
the field ``type`` of the ``res.partner`` model accept values contains
in ``['default', 'invoice', 'delivery', 'contact', 'other']``::

    >>> partner.type = 'delivery'   # Ok
    >>> partner.type = 'foobar'     # Error!
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/service/model/fields.py", line 148, in __set__
        value = self.check_value(value)
      File "odoorpc/service/model/fields.py", line 160, in check_value
        field_name=self.name,
    ValueError: The value 'foobar' supplied doesn't match with the possible values '['contact', 'invoice', 'delivery', 'other']' for the 'type' field

Many2one
''''''''

You can also update a ``many2one`` field, with either an ID or a record::

    >>> partner.parent_id = 1                   # with an ID
    >>> partner.parent_id = Partner.browse(1)   # with a record object

You can't put any ID or record, a check is made on the relationship
to ensure data integrity::

    >>> User = odoo.env['res.users']
    >>> user = User.browse(1)
    >>> partner = Partner.browse(2)
    >>> partner.parent_id = user
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/service/model/fields.py", line 263, in __set__
        o_rel = self.check_value(o_rel)
      File "odoorpc/service/model/fields.py", line 275, in check_value
        field_name=self.name))
    ValueError: Instance of 'res.users' supplied doesn't match with the relation 'res.partner' of the 'parent_id' field.

One2many and Many2many
''''''''''''''''''''''

``one2many`` and ``many2many`` fields can be updated by providing
a list of tuple as specified in the `Odoo` documentation
(`link <https://github.com/odoo/odoo/blob/10.0/odoo/models.py#L3479>`_),
a list of records, a list of record IDs, an empty list or ``False``:

With a tuple (as documented), no magic here::

    >>> user = odoo.env['res.users'].browse(1)
    >>> user.groups_id = [(6, 0, [8, 5, 6, 4])]

With a recordset::

    >>> groups = odoo.env['res.groups'].browse([8, 5, 6, 4])
    >>> user.groups_id = groups

With a list of record IDs::

    >>> user.groups_id = [8, 5, 6, 4]

The last two examples are equivalent to the first (they generate a
``(6, 0, IDS)`` tuple).

However, if you set an empty list or ``False``, the relation between records
will be removed::

    >>> user.groups_id = []
    >>> user.groups_id
    Recordset('res.group', [])
    >>> user.groups_id = False
    >>> user.groups_id
    Recordset('res.group', [])

Another facility provided by `OdooRPC` is adding and removing objects using
`Python` operators ``+=`` and ``-=``. As usual, you can add an ID,
a record, or a list of them:

With a list of records::

    >>> groups = odoo.env['res.groups'].browse([4, 5])
    Recordset('res.group', [1, 2, 3])
    >>> user.groups_id += groups
    >>> user.groups_id
    Recordset('res.group', [1, 2, 3, 4, 5])

With a list of record IDs::

    >>> user.groups_id += [4, 5]
    >>> user.groups_id
    Recordset('res.group', [1, 2, 3, 4, 5])

With an ID only::

    >>> user.groups_id -= 4
    >>> user.groups_id
    Recordset('res.group', [1, 2, 3, 5])

With a record only::

    >>> group = odoo.env['res.groups'].browse(5)
    >>> user.groups_id -= group
    >>> user.groups_id
    Recordset('res.group', [1, 2, 3])

Reference
'''''''''

To update a ``reference`` field, you have to use either a string or a record
object as below::

    >>> IrActionServer = odoo.env['ir.actions.server']
    >>> action_server = IrActionServer.browse(8)
    >>> action_server.ref_object = 'res.partner,1'      # with a string with the format '{relation},{id}'
    >>> action_server.ref_object = Partner.browse(1)    # with a record object

A check is made on the relation name::

    >>> action_server.ref_object = 'foo.bar,42'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/service/model/fields.py", line 370, in __set__
        value = self.check_value(value)
      File "odoorpc/service/model/fields.py", line 400, in check_value
        self._check_relation(relation)
      File "odoorpc/service/model/fields.py", line 381, in _check_relation
        field_name=self.name,
    ValueError: The value 'foo.bar' supplied doesn't match with the possible values '[...]' for the 'ref_object' field

Date and Datetime
'''''''''''''''''

``date`` and ``datetime`` fields accept either string values or
``datetime.date/datetime.datetime`` objects.

With ``datetime.date`` and ``datetime.datetime`` objects::

    >>> import datetime
    >>> Purchase = odoo.env['purchase.order']
    >>> order = Purchase.browse(1)
    >>> order.date_order = datetime.datetime(2016, 11, 7, 11, 23, 10)

With formated strings::

    >>> order.date_order = "2016-11-07"             # %Y-%m-%d
    >>> order.date_order = "2016-11-07 12:31:24"    # %Y-%m-%d %H:%M:%S

As always, a wrong type will raise an exception::

    >>> order.date_order = "foobar"
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/fields.py", line 187, in setter
        value = self.check_value(value)
      File "odoorpc/fields.py", line 203, in check_value
        self.pattern))
    ValueError: Value not well formatted, expecting '%Y-%m-%d %H:%M:%S' format

:ref:`Next step: Download reports <tuto-download-report>`
