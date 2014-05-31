# -*- coding: utf-8 -*-
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
"""Provides the :class:`ProxyJSON` class for JSON-RPC requests."""
import urllib2
import cookielib
import json
import random
import itertools
import mimetools
import mimetypes


class Proxy(object):
    """Base class to implement a proxy to perform requests."""
    def __init__(self, host, port, timeout=120, ssl=False, opener=None):
        self._root_url = "{http}{host}:{port}".format(
            http=(ssl and "https://" or "http://"), host=host, port=port)
        self._timeout = timeout
        self._builder = URLBuilder(self)
        self._opener = opener
        if not opener:
            cookie_jar = cookielib.CookieJar()
            self._opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(cookie_jar))

    def __getattr__(self, name):
        return getattr(self._builder, name)

    def __getitem__(self, url):
        return self._builder[url]


class ProxyJSON(Proxy):
    """The :class:`ProxyJSON` class provides a dynamic access
    to all JSON methods.
    """
    def __init__(self, host, port, timeout=120, ssl=False, opener=None,
                 deserialize=True):
        Proxy.__init__(self, host, port, timeout, ssl, opener)
        self._deserialize = deserialize

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


class ProxyHTTP(Proxy):
    """The :class:`ProxyHTTP` class provides a dynamic access
    to all HTTP methods.
    """
    def __call__(self, url, data, headers=None):
        request = urllib2.Request(url='/'.join([self._root_url, url]))
        request.add_data(data)
        if headers:
            for hkey in headers:
                hvalue = headers[hkey]
                request.add_header(hkey, hvalue)
        return self._opener.open(request, timeout=self._timeout)


class URLBuilder(object):
    """Auto-builds an URL while getting its attributes.
    Used by the :class:`ProxyJSON` and :class:`ProxyHTTP` classes.
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
