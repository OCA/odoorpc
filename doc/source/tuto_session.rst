.. _tuto-manage-sessions:

Save your credentials (session)
-------------------------------

Once you are authenticated with your :class:`ODOO <odoorpc.ODOO>` instance, you
can :func:`save <odoorpc.ODOO.save>` your credentials under a code name and use
this one to quickly instantiate a new :class:`ODOO <odoorpc.ODOO>` class::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost')
    >>> user = odoo.login('tutorial', 'admin', 'admin')
    >>> odoo.save('tutorial')

By default, these informations are stored in the ``~/.odoorpcrc`` file. You can
however use another file::

    >>> odoo.save('tutorial', '~/my_own_odoorpcrc')

Then, use the :func:`odoorpc.ODOO.load` class method::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO.load('tutorial')

Or, if you have saved your configuration in another file::

    >>> odoo = odoorpc.ODOO.load('tutorial', '~/my_own_odoorpcrc')

You can check available sessions with :func:`odoorpc.ODOO.list`, and remove
them with :func:`odoorpc.ODOO.remove`::

    >>> odoorpc.ODOO.list()
    ['tutorial']
    >>> odoorpc.ODOO.remove('tutorial')
    >>> 'tutorial' not in odoorpc.ODOO.list()
    True
