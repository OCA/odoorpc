.. _faq:

Frequently Asked Questions (FAQ)
================================

Why OdooRPC? And why migrate from OERPLib to OdooRPC?
-----------------------------------------------------

It was a tough decision, but several reasons motivated the `OdooRPC` project:

**RPC Protocol**
  The first point is about the supported protocol, `XML-RPC` is kept in `Odoo`
  for compatibility reasons (and will not evolve anymore, maybe removed one
  day), replaced by the `JSON-RPC` one. Although these
  protocols are almost similar in the way we build RPC requests, some points
  make `JSON-RPC` a better and reliable choice like the way to handle errors
  raised by the `Odoo` server (access to the type of exception raised, the
  complete server traceback...). To keep a clean and maintainable base code, it
  would have been difficult to support both protocols in `OERPLib`, and it is
  why `OdooRPC` only support `JSON-RPC`.

  Another good point with `JSON-RPC` is the ability to request all server web
  controllers to reproduce requests (`type='json'` ones) made by the official
  `Javascript` web client.
  As the code to make such requests is based on standard `HTTP` related Python
  modules, `OdooRPC` is also able to request `HTTP` web controllers
  (`type='http'` ones).

  In fact, you could see `OdooRPC` as a high level API for `Odoo` with which
  you could replicate the behaviour of the official `Javascript` web client,
  but in `Python`.

**New server API**
  One goal of `OERPLib` was to give an API not too different from the server
  side API to reduce the learning gap between server-side development and
  client-side with an `RPC` library. With the new API which appears in
  `Odoo` 8.0 this is another brake (the old API has even been removed
  since Odoo 10.0), so the current API of `OERPLib` is not anymore consistent.
  As such, `OdooRPC` mimics A LOT the new API of Odoo, for more
  consistency (see the :ref:`tutorials <tutorials>`).

**New brand Odoo**
  `OpenERP` became `Odoo`, so what does `OERPLib` mean? `OEWhat`? This is
  obvious for old developers which start the `OpenERP` adventure since the
  early days, but the `OpenERP` brand is led to disappear, and it can be
  confusing for newcomers in the `Odoo` world. So, `OdooRPC` speaks for
  itself.

**Maintenance cost, code cleanup**
  `OpenERP` has evolved a lot since the version 5.0 (2009), making `OERPLib`
  hard to maintain (write tests for all versions before each `OERPLib` and
  `OpenERP` release is very time consuming). All the compatibility code for
  `OpenERP` 5.0 to 7.0 was dropped for `OdooRPC`, making the project more
  maintainable. `Odoo` is now a more mature product, and `OdooRPC` should
  suffer less about compatibility issues from one release to another.

  As `OdooRPC` has not the same constraints concerning `Python`
  environments where it could be running on, it is able to work on `Python`
  2.7 to 3.X.

`OdooRPC` is turned towards the future, so you are encouraged to use or migrate
on it for projects based on `Odoo` >= 8.0. It is more reliable, better covered
by unit tests, and almost identical to the server side new API.


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

.. note:
    It is about the the old API (`on_change` statement declared in a XML view
    with its associated Python method).

`OdooRPC` does not provide helpers for such methods currently.
A call to an ``on_change`` method intend to be executed from a view and there
is no support for that (not yet?) such as fill a form, validate it, etc...

But you can emulate an ``on_change`` by writing your own function,
for instance::

    def on_change(record, method, args=None, kwargs=None):
        """Update `record` with the result of the on_change `method`"""
        res = record._odoo.execute_kw(record._name, method, args, kwargs)
        for k, v in res['value'].iteritems():
            setattr(record, k, v)

And call it on a record with the desired method and its parameters::

    >>> order = odoo.get('sale.order').browse(42)
    >>> on_change(order, 'product_id_change', args=[ARGS], kwargs={KWARGS})

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
        if v(odoo.version) < v('10.0'):
            pass  # do some stuff
        else:
            pass  # do something else
