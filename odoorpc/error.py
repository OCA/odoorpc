# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""This module contains all exceptions raised by `OdooRPC` when an error
occurred.
"""
import sys


class Error(Exception):
    """Base class for exception."""

    pass


class RPCError(Error):
    """Exception raised for errors related to RPC queries.
    Error details (like the `Odoo` server traceback) are available through the
    `info` attribute:

    .. doctest::
        :options: +SKIP

        >>> from pprint import pprint as pp
        >>> try:
        ...     odoo.execute('res.users', 'wrong_method')
        ... except odoorpc.error.RPCError as exc:
        ...     pp(exc.info)
        ...
        {'code': 200,
         'data': {'arguments': ["type object 'res.users' has no attribute 'wrong_method'"],
                  'debug': 'Traceback (most recent call last):\\n  File ...',
                  'exception_type': 'internal_error',
                  'message': "'res.users' object has no attribute 'wrong_method'",
                  'name': 'exceptions.AttributeError'}
         'message': 'Odoo Server Error'}

    .. doctest::
        :hide:

        >>> from pprint import pprint as pp
        >>> try:
        ...     odoo.execute('res.users', 'wrong_method')
        ... except odoorpc.error.RPCError as exc:
        ...     exc.info['code'] == 200
        ...     'message' in exc.info
        ...     exc.info['data']['arguments'] in [
        ...         ["'res.users' object has no attribute 'wrong_method'"],         # >= 8.0
        ...         ["type object 'res.users' has no attribute 'wrong_method'"],    # >= 10.0
        ...     ]
        ...     exc.info['data']['debug'].startswith('Traceback (most recent call last):\\n  File')
        ...     exc.info['data']['message'] in [
        ...         "'res.users' object has no attribute 'wrong_method'",           # >= 8.0
        ...         "type object 'res.users' has no attribute 'wrong_method'",      # >= 10.0
        ...     ]
        ...     exc.info['data']['name'] in [
        ...         'exceptions.AttributeError',
        ...         'builtins.AttributeError',
        ...     ]
        ...
        True
        True
        True
        True
        True
        True
    """

    def __init__(self, message, info=False):
        # Ensure that the message is in unicode,
        # to be compatible both with Python2 and 3
        try:
            message = message.decode('utf-8')
        except (UnicodeEncodeError, AttributeError):
            pass
        super(Error, self).__init__(message, info)
        self.info = info

    def __str__(self):
        # args[0] should always be a unicode object (see '__init__(...)')
        if sys.version_info[0] < 3 and self.args and self.args[0]:
            return self.args[0].encode('utf-8')
        return self.args and self.args[0] or ''

    def __unicode__(self):
        # args[0] should always be a unicode object (see '__init__(...)')
        return self.args and self.args[0] or u''

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.args[0]))


class InternalError(Error):
    """Exception raised for errors occurring during an internal operation."""

    pass
