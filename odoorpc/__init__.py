# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""The `odoorpc` module defines the :class:`ODOO` class.

The :class:`ODOO` class is the entry point to manage `Odoo` servers.
You can use this one to write `Python` programs that performs a variety of
automated jobs that communicate with a `Odoo` server.

Here's a sample session using this module::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost', port=8069)  # connect to localhost, default port
    >>> odoo.login('dbname', 'admin', 'admin')

To catch debug logs of OdooRPC from your own code, you have to configure
a logger the way you want with a log level set to `DEBUG`::

    >>> import logging
    >>> logging.basicConfig()
    >>> logger = logging.getLogger('odoorpc')
    >>> logger.setLevel(logging.DEBUG)

Then all queries generated by OdooRPC will be logged::

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO()
    >>> odoo.login('dbname', 'admin', 'admin')
    DEBUG:odoorpc.rpc.jsonrpclib:(JSON,send) http://localhost:8069/web/session/authenticate {'jsonrpc': '2.0', 'id': 499807971, 'method': 'call', 'params': {'db': 'dbname', 'login': 'admin', 'password': '**********'}}
    DEBUG:odoorpc.rpc.jsonrpclib:(JSON,recv) http://localhost:8069/web/session/authenticate {'jsonrpc': '2.0', 'id': 499807971, 'method': 'call', 'params': {'db': 'dbname', 'login': 'admin', 'password': '**********'}} => {'result': {'is_admin': True, 'server_version': '12.0-20181008', 'currencies': {'2': {'digits': [69, 2], 'position': 'before', 'symbol': '$'}, '1': {'digits': [69, 2], 'position': 'after', 'symbol': '€'}}, 'partner_display_name': 'YourCompany, Mitchell Admin', 'company_id': 1, 'username': 'admin', 'web_tours': [], 'user_companies': False, 'session_id': '61cb37d21771531f789bea631a03236aa21f06d4', 'is_system': True, 'server_version_info': [12, 0, 0, 'final', 0, ''], 'db': 'odoorpc_v12', 'name': 'Mitchell Admin', 'web.base.url': 'http://localhost:8069', 'user_context': {'lang': 'fr_FR', 'tz': 'Europe/Brussels', 'uid': 2}, 'odoobot_initialized': True, 'show_effect': 'True', 'partner_id': 3, 'uid': 2}, 'id': 499807971, 'jsonrpc': '2.0'}
"""

__author__ = 'ABF Osiell - Sebastien Alix'
__email__ = 'sebastien.alix@osiell.com'
__licence__ = 'LGPL v3'
__version__ = '0.8.0'

__all__ = ['ODOO', 'error']

import logging

from odoorpc import error
from odoorpc.odoo import ODOO

logging.getLogger(__name__).addHandler(logging.NullHandler())
