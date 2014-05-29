# -*- coding: UTF-8 -*-
##############################################################################
#
#    OdooRPC
#    Copyright (C) 2014 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""This module provides `RPC` connector which use the `JSON-RPC` protocol
to communicate with an `Odoo` server.

Afterwards, `RPC` services and their associated methods can be accessed
dynamically from this connector.
Here are the main services URLs:

==================  ======================================================
URL                 Description
==================  ======================================================
''/web/database''   Manage databases (create, drop, backup...)
''/web/session''    Manage the user session (authentication, logout...)
''/web/dataset''    Manage all kinds of data (model methods, workflows)
''/web/action''     Manage all kinds of action (act_window, report.xml...)
''/web/export''     Manage data exports
''/web/menu''       Access to menus related to the user connected
==================  ======================================================

"""
from odoorpc.rpc import error, jsonrpclib
from odoorpc.tools import v


class Connector(object):
    """Connector base class defining the interface used
    to interact with a server.
    """
    def __init__(self, server, port=8069, timeout=120, version=None):
        self.server = server
        try:
            int(port)
        except ValueError:
            txt = "The port '{0}' is invalid. An integer is required."
            txt = txt.format(port)
            raise error.ConnectorError(txt)
        else:
            self.port = int(port)
        self._timeout = timeout
        self.version = version
        self._url = None

    @property
    def timeout(self):
        """Return the timeout."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set the timeout."""
        self._timeout = timeout


class ConnectorJSONRPC(Connector):
    """Connector class using the `JSON-RPC` protocol.

    >>> from odoorpc import rpc
    >>> cnt = rpc.ConnectorJSONRPC('localhost', port=8069)

    Open a user session:

    >>> cnt.proxy.web.session.authenticate(db='database', login='admin', password='admin')
    {u'jsonrpc': u'2.0', u'id': 202516757,
     u'result': {u'username': u'admin', u'user_context': {u'lang': u'fr_FR', u'tz': u'Europe/Brussels', u'uid': 1},
     u'db': u'test70', u'uid': 1, u'session_id': u'308816f081394a9c803613895b988540'}}

    Read data of a partner:

    >>> cnt.proxy.web.dataset.call(model='res.partner', method='read', args=[[1]])
    {u'jsonrpc': u'2.0', u'id': 454236230,
     u'result': [{u'id': 1, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

    You can send requests this way too:

    >>> cnt.proxy['/web/dataset'].call(model='res.partner', method='read', args=[[1]])
    {u'jsonrpc': u'2.0', u'id': 328686288,
     u'result': [{u'id': 1, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

    Or like this:

    >>> cnt.proxy['web']['dataset'].call(model='res.partner', method='read', args=[[1]])
    {u'jsonrpc': u'2.0', u'id': 102320639,
     u'result': [{u'id': 1, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}
    """
    def __init__(self, server, port=8069, timeout=120, version=None,
                 deserialize=True):
        super(ConnectorJSONRPC, self).__init__(server, port, timeout, version)
        self.deserialize = deserialize
        self._proxy = self._get_proxy(ssl=False)

    def _get_proxy(self, ssl=False):
        """Returns a :class:`Proxy <odoorpc.rpc.jsonrpclib.Proxy>` instance
        corresponding to the server version used.
        """
        # Detect the server version
        if self.version is None:
            proxy = jsonrpclib.Proxy(
                self.server, self.port, self._timeout,
                ssl=ssl, deserialize=self.deserialize)
            result = proxy.web.webclient.version_info()['result']
            # Server 6.1
            if 'version' in result:
                self.version = result['version']
            # Server >= 7.0
            elif 'server_version' in result:
                self.version = result['server_version']
        return proxy

    @property
    def proxy(self):
        """Return the JSON-RPC proxy."""
        return self._proxy

    @property
    def timeout(self):
        """Return the timeout."""
        return self._proxy._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set the timeout."""
        self._proxy._timeout = timeout


class ConnectorJSONRPCSSL(ConnectorJSONRPC):
    """Connector class using the `JSON-RPC` protocol over `SSL`.

    >>> from odoorpc import rpc
    >>> cnt = rpc.ConnectorJSONRPCSSL('localhost', port=8069)
    """
    def __init__(self, server, port=8069, timeout=120, version=None,
                 deserialize=True):
        super(ConnectorJSONRPCSSL, self).__init__(
            server, port, timeout, version)
        self._proxy = self._get_proxy(ssl=True)


PROTOCOLS = {
    'jsonrpc': ConnectorJSONRPC,
    'jsonrpc+ssl': ConnectorJSONRPCSSL,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
