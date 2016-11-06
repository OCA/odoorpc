.. _tuto-login:

Login to your new database
**************************

Use the :func:`login <odoorpc.ODOO.login>` method on a database with the
account of your choice::

    >>> odoo.login('tutorial', 'admin', 'password')

.. note::

    Under the hood the login method creates a cookie, and all requests
    thereafter which need a user authentication are cookie-based.

Once logged in, you can check some information through the
:class:`environment <odoorpc.ODOO.env>`::

    >>> odoo.env.db
    'tutorial'
    >>> odoo.env.context
    {'lang': 'fr_FR', 'tz': 'Europe/Brussels', 'uid': 1}
    >>> odoo.env.uid
    1
    >>> odoo.env.lang
    'fr_FR'
    >>> odoo.env.user.name              # name of the user
    'Administrator'
    >>> odoo.env.user.company_id.name   # the name of its company
    'YourCompany'

From now, you can easily execute any kind of queries on your
`Odoo` server (execute model methods, trigger workflow, download reports...).

:ref:`Next step: Execute RPC queries <tuto-execute-queries>`
