.. _faq:

Frequently Asked Questions (FAQ) **(New in version 0.8)**
=========================================================

Connect to an OpenERP Online (SaaS) instance
--------------------------------------------

First, you have to connect on your `OpenERP` instance, and set a password for
your user account in order to active the `XML-RPC` protocol.

Then, just use the ``xmlrpc+ssl`` protocol with the port 443::

    >>> import oerplib
    >>> oerp = oerplib.OERP('foobar.my.openerp.com', protocol='xmlrpc+ssl', port=443)
    >>> oerp.db.server_version()
    '7.saas~1'

Update a record with an `on_change` method
------------------------------------------

`OERPLib` does not provide helpers for such methods currently.
A call to an ``on_change`` method intend to be executed from a view and there
is no support for that (not yet?) such as fill a form, validate it, etc...

But you can emulate an ``on_change`` by writing your own function,
for instance::

    def on_change(oerp, record, method, *args):
        """Update `record` with the result of the on_change `method`"""
        res = oerp.execute(record.__osv__['name'], method, *args)
        for k, v in res['value'].iteritems():
            setattr(record, k, v)
        return record

And call it on a record with the desired method and its parameters::

    >>> order = oerp.get('sale.order').browse(42)
    >>> order = on_change(oerp, order, 'product_id_change', ARGS...)
    >>> oerp.write_record(order)  # Save your record

To know what parameters to send to the ``on_change``, the
:func:`scan_on_change <oerplib.service.inspect.Inspect.scan_on_change>` method
can help you.

Some OSV methods does not accept the `context` parameter
--------------------------------------------------------

Since `OpenERP` 6.1, the ``context`` parameter can be sent automatically for
each call to an `OSV/Model` method (this is the default behaviour since
`OERPLib` 0.7). But on the side of the `OpenERP` server, some `OSV` methods
have no ``context`` parameter, and `OERPLib` has no way to guess it, which
results in an nasty exception. So you have to disable temporarily this behaviour
by yourself by setting the ``auto_context`` option to ``False``::

    >>> oerp.config['auto_context'] = False  # 'get()' method of 'ir.sequence' does not support the context parameter
    >>> next_seq = oerp.get('ir.sequence').get('stock.lot.serial')
    >>> oerp.config['auto_context'] = True  # Restore the configuration

Change the behaviour of a script according to the version of OpenERP
--------------------------------------------------------------------

You can compare versions of `OpenERP` servers with the
:func:`v <oerplib.tools.v>` function applied on the
:attr:`OERP.version <oerplib.OERP.version>` property, for instance::

    import oerplib
    from oerplib.tools import v

    for session in oerplib.OERP.list():
        oerp = oerplib.OERP.load(session)
        if v(oerp.version) <= v('6.1'):
            pass  # do some stuff
        else:
            pass  # do something else
