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
import json
import random
import sys
# Python 2
if sys.version_info[0] < 3:
    from urllib2 import build_opener, HTTPCookieProcessor, Request
    from cookielib import CookieJar

    def encode_data(data):
        return data

    def decode_data(data):
        return data
# Python >= 3
else:
    from urllib.request import build_opener, HTTPCookieProcessor, Request
    from http.cookiejar import CookieJar
    import io

    def encode_data(data):
        try:
            return bytes(data, 'utf-8')
        except:
            return bytes(data)

    def decode_data(data):
        return io.StringIO(data.read().decode('utf-8'))


class Proxy(object):
    """Base class to implement a proxy to perform requests."""
    def __init__(self, host, port, timeout=120, ssl=False, opener=None):
        self._root_url = "{http}{host}:{port}".format(
            http=(ssl and "https://" or "http://"), host=host, port=port)
        self._timeout = timeout
        self._builder = URLBuilder(self)
        self._opener = opener
        if not opener:
            cookie_jar = CookieJar()
            self._opener = build_opener(HTTPCookieProcessor(cookie_jar))

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
        if url.startswith('/'):
            url = url[1:]
        request = Request(url='/'.join([self._root_url, url]),
                          data=encode_data(data))
        request.add_header('Content-Type', 'application/json')
        response = self._opener.open(request, timeout=self._timeout)
        if not self._deserialize:
            return response
        return json.load(decode_data(response))


class ProxyHTTP(Proxy):
    """The :class:`ProxyHTTP` class provides a dynamic access
    to all HTTP methods.
    """
    def __call__(self, url, data=None, headers=None):
        if url.startswith('/'):
            url = url[1:]
        kwargs = {
            'url': '/'.join([self._root_url, url]),
        }
        if data:
            kwargs['data'] = encode_data(data)
        request = Request(**kwargs)
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
