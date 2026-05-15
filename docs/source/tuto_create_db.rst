Create a new database
*********************

To dialog with your `Odoo` server, you need an instance of the
:class:`odoorpc.ODOO` class. Let's instanciate it::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost', 'jsonrpc', 8069)

Two protocols are available: ``jsonrpc`` and ``jsonrpc+ssl``.
Then, create your database for the purposes of this tutorial (you need to
know the `super` admin password to do this)::

    >>> odoo.db.create('super_password', 'tutorial', demo=True, lang='fr_FR', admin_password='password')

The creation process may take some time on the server. If you get a timeout
error, set a higher timeout before repeating the process::

    >>> odoo.config['timeout'] = 300    # Set the timeout to 300 seconds
    >>> odoo.db.create('super_password', 'tutorial', demo=True, lang='fr_FR', admin_password='password')

To check available databases, use the :attr:`odoo.db <odoorpc.ODOO.db>`
property with the :func:`list <odoorpc.db.DB.list>` method::

    >>> odoo.db.list()
    ['tutorial']

You are now ready to login to your database!

Documentation about databases management is available
:class:`here <odoorpc.db.DB>`.

:ref:`Next step: Login to your new database <tuto-login>`
