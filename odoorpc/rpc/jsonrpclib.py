# -*- coding: utf-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2013 Sébastien Alix.
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
"""Provides the :class:`Proxy` and :class:`ProxyLegacy` classes."""
import urllib2
import cookielib
import json
import random


class Proxy(object):
    """The :class:`Proxy` class provides a dynamic access
    to all JSON methods.
    """
    def __init__(self, host, port, timeout=120, ssl=False, deserialize=True):
        self._root_url = "{http}{host}:{port}".format(
            http=(ssl and "https://" or "http://"), host=host, port=port)
        self._timeout = timeout
        self._deserialize = deserialize
        self._builder = URLBuilder(self)
        cookie_jar = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookie_jar))

    def __getattr__(self, name):
        return getattr(self._builder, name)

    def __getitem__(self, url):
        return self._builder[url]

    def __call__(self, url, params):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
            "id": random.randint(0, 1000000000),
        })
        request = urllib2.Request(url='/'.join([self._root_url, url]))
        request.add_header('Content-Type', 'application/json')
        request.add_data(data)
        response = self._opener.open(request, timeout=self._timeout)
        if not self._deserialize:
            return response
        return json.load(response)


class ProxyLegacy(Proxy):
    """The :class:`ProxyLegacy` class fixes the request handling for
    OpenERP 6.1 and 7.0 by adding automatically the ``session_id`` parameter
    once the user is authenticated.
    """
    def __init__(self, host, port, timeout=120, ssl=False, deserialize=True):
        super(ProxyLegacy, self).__init__(host, port, timeout, ssl, deserialize)
        self._session_id = None

    def __call__(self, url, params):
        """Overloads the :func:`Proxy.__call__` method to add the 'session_id'
        parameter if necessary.
        """
        if url == 'web/session/authenticate':
            response = super(ProxyLegacy, self).__call__(url, params)
            result = self._deserialize and response or json.load(response)
            self._session_id = result and result['result']['session_id']
            return response
        elif self._session_id and 'session_id' not in params:
            params['session_id'] = self._session_id
        return super(ProxyLegacy, self).__call__(url, params)


class URLBuilder(object):
    """Auto-builds an URL while getting its attributes.
    Used by :class:`Proxy` and :class:`ProxyLegacy` classes.
    """
    def __init__(self, rpc, url=None):
        self._rpc = rpc
        self._url = url

    def __getattr__(self, path):
        new_url = self._url and '/'.join([self._url, path]) or path
        return URLBuilder(self._rpc, new_url)

    def __getitem__(self, path):
        if path and path[0] == '/':
            path = path[1:]
        if path and path[-1] == '/':
            path = path[:-1]
        return getattr(self, path)

    def __call__(self, **kwargs):
        return self._rpc(self._url, kwargs)

    def __str__(self):
        return self._url
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
