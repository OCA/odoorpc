odoorpc
=======

.. automodule:: odoorpc

Here's a sample session using this module::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost', port=8069)  # connect to localhost, default port
    >>> odoo.login('my_database', 'admin', 'admin')
