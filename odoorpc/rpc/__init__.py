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
"""This module provides `Proxy` classes to communicate with an `Odoo` server
with the `JSON-RPC` protocol or through simple HTTP requests.

On `Odoo` server, web controllers expose two kinds of methods: `json`
and `http`. These methods can be accessed from the proxy classes of this module.
Here are the main services URLs:

==================  ======================================================
URL                 Description
==================  ======================================================
``/web/database``   Manage databases (create, drop, backup...)
``/web/session``    Manage the user session (authentication, logout...)
``/web/webclient``  Retrieve information about the server version
``/web/dataset``    Manage all kinds of data (model methods, workflows)
``/web/action``     Manage all kinds of action (act_window, report.xml...)
``/web/export``     Manage data exports
``/web/menu``       Access to menus related to the user connected
==================  ======================================================

"""
import urllib2
import cookielib

from odoorpc.rpc import error, jsonrpclib
from odoorpc.tools import v


class Connector(object):
    """Connector base class defining the interface used
    to interact with a server.
    """
    def __init__(self, host, port=8069, timeout=120, version=None):
        self.host = host
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

    @property
    def ssl(self):
        """Return `True` if SSL is activated."""
        return False

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

    >>> cnt.proxy_json.web.session.authenticate(db='database', login='admin', password='admin')
    {u'jsonrpc': u'2.0', u'id': 202516757,
     u'result': {u'username': u'admin', u'user_context': {u'lang': u'fr_FR', u'tz': u'Europe/Brussels', u'uid': 1},
     u'db': u'test70', u'uid': 1, u'session_id': u'308816f081394a9c803613895b988540'}}

    Read data of a partner:

    >>> cnt.proxy_json.web.dataset.call(model='res.partner', method='read', args=[[1]])
    {u'jsonrpc': u'2.0', u'id': 454236230,
     u'result': [{u'id': 1, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

    You can send requests this way too:

    >>> cnt.proxy_json['/web/dataset/call'](model='res.partner', method='read', args=[[1]])
    {u'jsonrpc': u'2.0', u'id': 328686288,
     u'result': [{u'id': 1, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}

    Or like this:

    >>> cnt.proxy_json['web']['dataset']['call'](model='res.partner', method='read', args=[[1]])
    {u'jsonrpc': u'2.0', u'id': 102320639,
     u'result': [{u'id': 1, u'comment': False, u'ean13': False, u'property_account_position': False, ...}]}
    """
    def __init__(self, host, port=8069, timeout=120, version=None,
                 deserialize=True):
        super(ConnectorJSONRPC, self).__init__(host, port, timeout, version)
        self.deserialize = deserialize
        # One URL opener (with cookies handling) shared between
        # JSON and HTTP requests
        cookie_jar = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookie_jar))
        self._proxy_json, self._proxy_http = self._get_proxies()

    def _get_proxies(self):
        """Returns the :class:`ProxyJSON <odoorpc.rpc.jsonrpclib.ProxyJSON>`
        and :class:`ProxyHTTP <odoorpc.rpc.jsonrpclib.ProxyHTTP>` instances
        corresponding to the server version used.
        """
        proxy_json = jsonrpclib.ProxyJSON(
            self.host, self.port, self._timeout,
            ssl=self.ssl, deserialize=self.deserialize, opener=self._opener)
        proxy_http = jsonrpclib.ProxyHTTP(
            self.host, self.port, self._timeout,
            ssl=self.ssl, opener=self._opener)
        # Detect the server version
        if self.version is None:
            result = proxy_json.web.webclient.version_info()['result']
            if 'server_version' in result:
                self.version = result['server_version']
        return proxy_json, proxy_http

    @property
    def proxy_json(self):
        """Return the JSON proxy."""
        return self._proxy_json

    @property
    def proxy_http(self):
        """Return the HTTP proxy."""
        return self._proxy_http

    @property
    def timeout(self):
        """Return the timeout."""
        return self._proxy_json._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set the timeout."""
        self._proxy_json._timeout = timeout
        self._proxy_http._timeout = timeout


class ConnectorJSONRPCSSL(ConnectorJSONRPC):
    """Connector class using the `JSON-RPC` protocol over `SSL`.

    >>> from odoorpc import rpc
    >>> cnt = rpc.ConnectorJSONRPCSSL('localhost', port=8069)
    """
    def __init__(self, host, port=8069, timeout=120, version=None,
                 deserialize=True):
        super(ConnectorJSONRPCSSL, self).__init__(host, port, timeout, version)
        self._proxy_json, self._proxy_http = self._get_proxies()

    @property
    def ssl(self):
        return True


PROTOCOLS = {
    'jsonrpc': ConnectorJSONRPC,
    'jsonrpc+ssl': ConnectorJSONRPCSSL,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
