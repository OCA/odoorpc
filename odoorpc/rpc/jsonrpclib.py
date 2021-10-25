# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""Provides the :class:`ProxyJSON` class for JSON-RPC requests."""
import copy
import json
import logging
import random
import sys

# Python 2
if sys.version_info[0] < 3:
    from cookielib import CookieJar
    from urllib2 import HTTPCookieProcessor, Request, build_opener

    def encode_data(data):
        return data

    def decode_data(data):
        return data


# Python >= 3
else:
    import io
    from http.cookiejar import CookieJar
    from urllib.request import HTTPCookieProcessor, Request, build_opener

    def encode_data(data):
        try:
            return bytes(data, 'utf-8')
        except:  # noqa: E722
            return bytes(data)

    def decode_data(data):
        return io.StringIO(data.read().decode('utf-8'))


LOG_HIDDEN_JSON_PARAMS = ['password']
LOG_JSON_SEND_MSG = u"(JSON,send) %(url)s %(data)s"
LOG_JSON_RECV_MSG = u"(JSON,recv) %(url)s %(data)s => %(result)s"
LOG_HTTP_SEND_MSG = u"(HTTP,send) %(url)s%(data)s"
LOG_HTTP_RECV_MSG = u"(HTTP,recv) %(url)s%(data)s => %(result)s"

logger = logging.getLogger(__name__)


def get_json_log_data(data):
    """Returns a new `data` dictionary with hidden params
    for log purpose.
    """
    log_data = data
    for param in LOG_HIDDEN_JSON_PARAMS:
        if param in data['params']:
            if log_data is data:
                log_data = copy.deepcopy(data)
            log_data['params'][param] = "**********"
    return log_data


class Proxy(object):
    """Base class to implement a proxy to perform requests."""

    def __init__(self, host, port, timeout=120, ssl=False, opener=None):
        self._root_url = "{http}{host}:{port}".format(
            http=(ssl and "https://" or "http://"), host=host, port=port
        )
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

    def _get_full_url(self, url):
        return '/'.join([self._root_url, url])


class ProxyJSON(Proxy):
    """The :class:`ProxyJSON` class provides a dynamic access
    to all JSON methods.
    """

    def __init__(
        self, host, port, timeout=120, ssl=False, opener=None, deserialize=True
    ):
        Proxy.__init__(self, host, port, timeout, ssl, opener)
        self._deserialize = deserialize

    def __call__(self, url, params=None):
        if params is None:
            params = {}
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
            "id": random.randint(0, 1000000000),
        }
        if url.startswith('/'):
            url = url[1:]
        full_url = self._get_full_url(url)
        log_data = get_json_log_data(data)
        logger.debug(LOG_JSON_SEND_MSG, {'url': full_url, 'data': log_data})
        data_json = json.dumps(data)
        request = Request(url=full_url, data=encode_data(data_json))
        request.add_header('Content-Type', 'application/json')
        response = self._opener.open(request, timeout=self._timeout)
        if not self._deserialize:
            return response
        result = json.load(decode_data(response))
        logger.debug(
            LOG_JSON_RECV_MSG,
            {'url': full_url, 'data': log_data, 'result': result},
        )
        return result


class ProxyHTTP(Proxy):
    """The :class:`ProxyHTTP` class provides a dynamic access
    to all HTTP methods.
    """

    def __call__(self, url, data=None, headers=None):
        if url.startswith('/'):
            url = url[1:]
        full_url = self._get_full_url(url)
        logger.debug(
            LOG_HTTP_SEND_MSG,
            {'url': full_url, 'data': data and u" (%s)" % data or u""},
        )
        kwargs = {'url': full_url}
        if data:
            kwargs['data'] = encode_data(data)
        request = Request(**kwargs)
        if headers:
            for hkey in headers:
                hvalue = headers[hkey]
                request.add_header(hkey, hvalue)
        response = self._opener.open(request, timeout=self._timeout)
        logger.debug(
            LOG_HTTP_RECV_MSG,
            {
                'url': full_url,
                'data': data and u" (%s)" % data or u"",
                'result': response,
            },
        )
        return response


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
