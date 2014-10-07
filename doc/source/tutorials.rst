.. _tutorials:

Tutorials
=========

First step: prepare the connection and login
--------------------------------------------

You need an instance of the :class:`ODOO <odoorpc.ODOO` class to dialog with an
`Odoo` server. Let's pretend that you want to connect as `admin` on
the `db_name` database of your local server. First, prepare the connection::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO(host='localhost', protocol='xmlrpc', port=8069)

To check databases available, use the
:attr:`odoo.database <odoorpc.ODOO.database` attribute with the
**get_list** method::

    >>> odoo.database.get_list()
    ['db_name', 'db_name2', ...]

The connection is ready, you are able to log in on the server with the account
of your choice::

    >>> user = odoo.login(db='db_name', login='admin', password='admin')

The ``login`` method returns an object representing the user connected.
It is built from the server-side model ``res.users``, and all its
informations are accessible (see :ref:`browse-records` section)::

    >>> print(user.name)            # print the full name of the user
    >>> print(user.company_id.name) # print the name of its company

Now you are connected, you can easily execute any kind of `RPC` queries on your
server (execute model methods, trigger workflow, download reports...).

.. _tutorials-execute-queries:

Execute queries
---------------

The basic methods to execute queries related to data models is
:func:`execute <odoorpc.ODOO.execute>` and
:func:`execute_kw <odoorpc.ODOO.execute_kw>`.
They takes at least two parameters (the model and method names)
following by variable parameters according to the method called::

    >>> order_data = odoo.execute('sale.order', 'read', [1], ['name'])

This instruction will call the ``read`` method of the model ``sale.order``
with the parameters ``[1]`` (list of record IDs) and ``['name']`` (list of
fields to return).

However there is a more efficient way to perform methods of a model, with the
:func:`get <odoorpc.ODOO.get>` method, which provides an API
almost syntactically identical to the `Odoo` server side API
(see :class:`odoorpc.service.model.Model`), and which is able to send the user
context automatically::

    >>> user_obj = odoo.get('res.users')
    >>> user_obj.write([1], {'name': "Dupont D."})
    True
    >>> context = user_obj.context_get()
    >>> context
    {'lang': 'fr_FR', 'tz': False}
    >>> product_obj = odoo.get('product.product')
    >>> product_obj.name_get([3, 4])
    [[3, '[PC1] PC Basic'], [4, u'[PC2] Basic+ PC (assembl\xe9 sur commande)']]

To stop sending the user context, use the :attr:`odoorpc.ODOO.config` property::

    >>> odoo.config['auto_context'] = False
    >>> product_obj.name_get([3, 4])    # Without context, lang 'en_US' by default
    [[3, '[PC1] Basic PC'], [4, '[PC2] Basic+ PC (assembly on order)']]

.. note::

    The ``auto_context`` option only affect model methods.

Here is another example of how to install a module (you have to be logged
as an administrator to perform this task)::

    >>> module_obj = odoo.get('ir.module.module')
    >>> module_id = module_obj.search([('name', '=', 'purchase')])
    >>> module_obj.button_immediate_install(module_id)

.. _browse-records:

Browse records
--------------

A great functionality of `OdooRPC` is its ability to generate objects that are
similar to browsable records used on the server side. All of this
is possible using the :func:`browse <odoorpc.service.model.Model.browse>`
method::

    # fetch one record
    partner_obj = odoo.get('res.partner')
    partner = partner_obj.browse(1)     # Partner ID = 1
    print(partner.name)
    # fetch several records
    for partner in partner_obj.browse([1, 2]):
        print(partner.name)

From such objects, it is possible to easily explore relationships. The related
records are generated on the fly::

    partner = partner_obj.browse(3)
    for child in partner.child_ids:
        print(child.name)

Outside relation fields, `Python` data types are used, like ``datetime.date``
and ``datetime.datetime``::

    >>> purchase_obj = odoo.get('purchase.order')
    >>> order = purchase_obj.browse(42)
    >>> order.minimum_planned_date
    datetime.datetime(2012, 3, 10, 0, 0)
    >>> order.date_order
    datetime.date(2012, 3, 8)

A list of data types used by ``browse_record`` fields are
available :ref:`here <fields>`.


Update data through browsable records
-------------------------------------

Update data of a browsable record is workable with the
:func:`write_record <odoorpc.ODOO.write_record>` method of an
:class:`ODOO <odoorpc.ODOO>` instance. Let's update the name of a partner::

    >>> partner.name = "Caporal Jones"
    >>> odoo.write_record(partner)

This is equivalent to::

    >>> partner_obj.write([partner.id], {'name': "Caporal Jones"})

Char, Float, Integer, Boolean, Text and Binary
''''''''''''''''''''''''''''''''''''''''''''''

As see above, it's as simple as that::

    >>> partner.name = "New Name"
    >>> odoo.write_record(partner)

Selection
'''''''''

Same as above, except there is a check about the value assigned. For instance,
the field ``type`` of the ``res.partner`` model accept values contains
in ``['default', 'invoice', 'delivery', 'contact', 'other']``::

    >>> partner.type = 'default' # Ok
    >>> partner.type = 'foobar'  # Error!
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/service/model/fields.py", line 148, in __set__
        value = self.check_value(value)
      File "odoorpc/service/model/fields.py", line 160, in check_value
        field_name=self.name,
    ValueError: The value 'foobar' supplied doesn't match with the possible values '[u'default', u'invoice', u'delivery', u'contact', u'other']' for the 'type' field

Many2One
''''''''

You can also update a ``many2one`` field, with either an ID or a browsable
record::

    >>> partner.parent_id = 1 # with an ID
    >>> odoo.write_record(partner)
    >>> parent = partner_obj.browse(1)  # with a browsable record
    >>> partner.parent_id = parent
    >>> odoo.write_record(partner)

You can't put any ID or browsable record, a check is made on the relationship
to ensure data integrity::

    >>> user_obj = odoo.get('res.users')
    >>> user = user_obj.browse(1)
    >>> partner = partner_obj.browse(2)
    >>> partner.parent_id = user
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/service/model/fields.py", line 263, in __set__
        o_rel = self.check_value(o_rel)
      File "odoorpc/service/model/fields.py", line 275, in check_value
        field_name=self.name))
    ValueError: Instance of 'res.users' supplied doesn't match with the relation 'res.partner' of the 'parent_id' field.

One2Many and Many2Many
''''''''''''''''''''''

``one2many`` and ``many2many`` fields can be updated by providing
a list of tuple as specified in the `OpenERP/Odoo` documentation, a list of
records, a list of record IDs or an empty list or ``False``:

With a tuple (as documented), no magic here::

    >>> user = odoo.get('res.users').browse(1)
    >>> user.groups_id = [(6, 0, [8, 5, 6, 4])]
    >>> odoo.write_record(user)

With a list of records::

    >>> user = odoo.get('res.users').browse(1)
    >>> groups = odoo.get('res.groups').browse([8, 5, 6, 4])
    >>> user.groups_id = list(groups)
    >>> odoo.write_record(user)

With a list of record IDs::

    >>> user = odoo.get('res.users').browse(1)
    >>> user.groups_id = [8, 5, 6, 4]
    >>> odoo.write_record(user)

The last two examples are equivalent to the first (they generate a
``(6, 0, IDS)`` tuple).

However, if you set an empty list or ``False``, a ``(5, )`` tuple will be
generated to cut the relation between records::

    >>> user = odoo.get('res.users').browse(1)
    >>> user.groups_id = []
    >>> list(user.groups_id)
    []
    >>> user.__data__['updated_values']['groups_id']
    [(5,)]
    >>> user.groups_id = False
    >>> list(user.groups_id)
    []
    >>> user.__data__['updated_values']['groups_id']
    [(5,)]

Another facility provided by `OdooRPC` is adding and removing objects using
`Python` operators ``+=`` and ``-=``. As usual, you can add an ID,
a record, or a list of them:

With a list of records::

    >>> user = odoo.get('res.users').browse(1)
    >>> groups = odoo.get('res.groups').browse([4, 5])
    >>> user.groups_id += list(groups)
    >>> [g.id for g in user.groups_id]
    [1, 2, 3, 4, 5]

With a list of record IDs::

    >>> user.groups_id += [4, 5]
    >>> [g.id for g in user.groups_id]
    [1, 2, 3, 4, 5]

With an ID only::

    >>> user.groups_id -= 4
    >>> [g.id for g in user.groups_id]
    [1, 2, 3, 5]

With a record only::

    >>> group = odoo.get('res.groups').browse(5)
    >>> user.groups_id -= group
    >>> [g.id for g in user.groups_id]
    [1, 2, 3]

Reference
'''''''''

To update a ``reference`` field, you have to use either a string or a browsable
record as below::

    >>> action_server_obj = odoo.get('ir.actions.server')
    >>> action_server = action_server_obj.browse(7)
    >>> action_server.ref_object = 'res.partner,1' # with a string with the format '{relation},{id}'
    >>> odoo.write_record(action_server)
    >>> partner = partner_obj.browse(1)
    >>> action_server.ref_object = partner  # with a browsable record
    >>> odoo.write_record(action_server)

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
    >>> purchase_obj = odoo.get('purchase.order')
    >>> order = purchase_obj.browse(42)
    >>> order.date_order = datetime.date(2011, 9, 20)
    >>> order.minimum_planned_date = datetime.datetime(2011, 9, 20, 12, 31, 24)
    >>> odoo.write_record(order)

With formated strings::

    >>> order.date_order = "2011-09-20"                     # %Y-%m-%d
    >>> order.minimum_planned_date = "2011-09-20 12:31:24"  # %Y-%m-%d %H:%M:%S
    >>> odoo.write_record(order)

As always, a wrong type will raise an exception::

    >>> order.date_order = "foobar"
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "odoorpc/fields.py", line 187, in setter
        value = self.check_value(value)
      File "odoorpc/fields.py", line 203, in check_value
        self.pattern))
    ValueError: Value not well formatted, expecting '%Y-%m-%d' format

Generate reports
----------------

Another nice functionnality is the reports generation with the
:attr:`report <odoorpc.ODOO.report>` property. The
:func:`download <odoorpc.service.report.Report.download>` method allows you to
retrieve a report from `Odoo` (in PDF, HTML... depending of the report).
You have to supply the name of the report and the list of record IDs to print::

    >>> report = odoo.report.download('product.product.label', [1, 2])

The method will return a file object response, you will have to read its
content in order to save it on your filesystem::

    >>> with open('labels.pdf', 'w') as report_file:
    ...     report_file.write(report.read())
    ...

Also, you can find useful information such as the file name and its type in the
response headers::

    >>> from pprint import pprint
    >>> pprint(dict(report.headers))
    {'content-disposition': "attachment; filename*=UTF-8''Products%20Labels.pdf",
     'content-length': '21646',
     'content-type': 'application/pdf',
     'date': 'Sun, 06 Jul 2014 19:01:45 GMT',
     'server': 'Werkzeug/0.8.3 Python/2.7.3',
     'set-cookie': 'fileToken=None; Path=/, session_id=ced9505769fedbb1a93359f12e80c45ce782f3e2; expires=Sat, 04-Oct-2014 19:01:45 GMT; Max-Age=7776000; Path=/'}

To consult available reports classified by data models, use the
:func:`get_list <odoorpc.service.report.Report.get_list>` method::

    >>> odoo.report.get_list()['sale.order']
    [{u'report_name': u'sale.report_saleorder', u'name': u'Quotation / Order'}]

Manage databases
----------------

You can manage server databases with the :attr:`odoorpc.ODOO.database` property.
It offers you methods to list, create, drop, dump, restore databases and so on.

.. note::
    You have not to be logged to perform database management tasks.
    Instead, you have to use the "super admin" password.

Prepare a connection::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost')

At this point, you are able to list databases of this server::

    >>> odoo.database.get_list()
    []

Let's create a new database::

    >>> odoo.database.create('super_admin_passwd', 'test_db', demo=False, lang='fr_FR')

The creation process may take some time on the server. When it is finished, you
can log in::

    >>> odoo.login('test_db', 'admin', 'admin')

Documentation about all methods is available here
:class:`here <odoorpc.service.database.Database`.

Save the session to open it quickly later
-----------------------------------------

Once you are authenticated with your :class:`ODOO <odoorpc.ODOO>` instance, you
can :func:`save <odoorpc.ODOO.save>` these connection information under a code
name and use this one to quickly instanciate a new :class:`ODOO <odoorpc.ODOO>`
class::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost')
    >>> user = odoo.login('admin', 'admin', 'my_database')
    >>> odoo.save('foo')

By default, these informations are stored in the ``~/.odoorpcrc`` file. You can
however use another file::

    >>> odoo.save('foo', '~/my_own_odoorpcrc')

Then, use the :func:`odoorpc.ODOO.load` class method::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO.load('foo')

Or, if you have saved your configuration in another file::

    >>> odoo = odoorpc.ODOO.load('foo', '~/my_own_odoorpcrc')

You can check available sessions with :func:`odoorpc.ODOO.list`, and remove
them with :func:`odoorpc.ODOO.remove`::

    >>> odoorpc.ODOO.list()
    ['foo']
    >>> odoorpc.ODOO.remove('foo')
    >>> 'foo' not in odoorpc.ODOO.list()
    True

Change the timeout
------------------

By default, the timeout is set to 120 seconds for all RPC requests.
If your requests need a higher timeout, you can set it through the
:attr:`odoorpc.ODOO.config` property::

    >>> odoo.config['timeout']
    120
    >>> odoo.config['timeout'] = 300  # Set the timeout to 300 seconds

