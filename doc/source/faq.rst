.. _faq:

Frequently Asked Questions (FAQ)
================================

Connect to an Odoo Online (SaaS) instance
-----------------------------------------

First, you have to connect on your `Odoo` instance, and set a password for
your user account in order to active the `RPC` interface.

Then, just use the ``jsonrpc+ssl`` protocol with the port 443::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('foobar.my.odoo.com', protocol='jsonrpc+ssl', port=443)
    >>> odoo.version
    '8.saas~5'

Update a record with an `on_change` method
------------------------------------------

`OdooRPC` does not provide helpers for such methods currently.
A call to an ``on_change`` method intend to be executed from a view and there
is no support for that (not yet?) such as fill a form, validate it, etc...

But you can emulate an ``on_change`` by writing your own function,
for instance::

    def on_change(odoo, record, method, *args):
        """Update `record` with the result of the on_change `method`"""
        res = odoo.execute(record.__osv__['name'], method, *args)
        for k, v in res['value'].iteritems():
            setattr(record, k, v)
        return record

And call it on a record with the desired method and its parameters::

    >>> order = odoo.get('sale.order').browse(42)
    >>> order = on_change(odoo, order, 'product_id_change', ARGS...)
    >>> odoo.write_record(order)  # Save your record

Some model methods does not accept the `context` parameter
----------------------------------------------------------

The ``context`` parameter is sent automatically for each call to a `Model`
method. But on the side of the `Odoo` server, some methods have no ``context``
parameter, and `OdooRPC` has no way to guess it, which results in an nasty
exception. So you have to disable temporarily this behaviour by yourself by
setting the ``auto_context`` option to ``False``::

    >>> odoo.config['auto_context'] = False  # 'get()' method of 'ir.sequence' does not support the context parameter
    >>> next_seq = odoo.get('ir.sequence').get('stock.lot.serial')
    >>> odoo.config['auto_context'] = True  # Restore the configuration

Change the behaviour of a script according to the version of Odoo
-----------------------------------------------------------------

You can compare versions of `Odoo` servers with the :func:`v <odoorpc.tools.v>`
function applied on the :attr:`ODOO.version <odoorpc.ODOO.version>` property,
for instance::

    import odoorpc
    from odoorpc.tools import v

    for session in odoorpc.ODOO.list():
        odoo = odoorpc.ODOO.load(session)
        if v(odoo.version) > v('8.0'):
            pass  # do some stuff
        else:
            pass  # do something else
