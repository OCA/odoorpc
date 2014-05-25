# -*- coding: UTF-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2011-2013 Sébastien Alix.
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

import xmlrpclib

from oerplib.rpc import netrpclib, xmlrpclib_custom, error


class ServiceXMLRPC(object):
    def __init__(self, connector, name, url):
        self._connector = connector
        self._name = name
        self._url = url

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                self._sock = xmlrpclib_custom.TimeoutServerProxy(
                    self._url, allow_none=True,
                    timeout=self._connector.timeout)
                sock_method = getattr(self._sock, method, False)
                return sock_method(*args)
            #NOTE: exception raised with these kind of requests:
            #   - execute('fake.model', 'search', [])
            #   - execute('sale.order', 'fake_method')
            except xmlrpclib.Fault as exc:
                # faultCode: error message
                # faultString: Server traceback (following the server version
                # used, a bad request can produce a server traceback, or not).
                raise error.ConnectorError(exc.faultCode, exc.faultString)
            #TODO NEED TEST (when is raised this exception?)
            except xmlrpclib.Error as exc:
                raise error.ConnectorError(' - '.join(exc.args))
        return rpc_method


class ServiceNetRPC(object):
    def __init__(self, connector, name, server, port):
        self._connector = connector
        self._name = name
        self._server = server
        self._port = port

    def __getattr__(self, method):
        def rpc_method(*args):
            try:
                sock = netrpclib.NetRPC(timeout=self._connector.timeout)
                sock.connect(self._server, self._port)
                sock.send((self._name, method, ) + args)
                result = sock.receive()
                sock.disconnect()
                return result
            #NOTE: exception raised with these kind of requests:
            #   - execute('fake.model', 'search', [])
            #   - execute('sale.order', 'fake_method')
            except netrpclib.NetRPCError as exc:
                # faultCode: error message
                # faultString: Server traceback (following the server version
                # used, a bad request can produce a server traceback, or not).
                raise error.ConnectorError(exc.faultCode, exc.faultString)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
