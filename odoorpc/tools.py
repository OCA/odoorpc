# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""This module contains the :class:`Config <odoorpc.config.Config>` class which
manage the configuration related to an instance of
:class:`ODOO <odoorpc.ODOO>`, and some useful helper functions used internally
in `OdooRPC`.
"""
try:
    from collections.abc import MutableMapping
except ImportError:  # Python 2.7 compatibility
    from collections import MutableMapping
import re

from .error import InternalError

MATCH_VERSION = re.compile(r'[^\d.]')


class Config(MutableMapping):
    """Class which manage the configuration of an
    :class:`ODOO <odoorpc.ODOO>` instance.

    .. note::
        This class have to be used through the :attr:`odoorpc.ODOO.config`
        property.

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost')    # doctest: +SKIP
    >>> type(odoo.config)
    <class 'odoorpc.tools.Config'>
    """

    def __init__(self, odoo, options):
        super(Config, self).__init__()
        self._odoo = odoo
        self._options = options or {}

    def __getitem__(self, key):
        return self._options[key]

    def __setitem__(self, key, value):
        """Handle ``timeout`` option to set the timeout on the connector."""
        if key == 'timeout':
            self._odoo._connector.timeout = value
        self._options[key] = value

    def __delitem__(self, key):
        raise InternalError("Operation not allowed")

    def __iter__(self):
        return self._options.__iter__()

    def __len__(self):
        return len(self._options)

    def __str__(self):
        return self._options.__str__()

    def __repr__(self):
        return self._options.__repr__()


def clean_version(version):
    """Clean a version string.

        >>> from odoorpc.tools import clean_version
        >>> clean_version('7.0alpha-20121206-000102')
        '7.0'

    :return: a cleaner version string
    """
    version = MATCH_VERSION.sub('', version.split('-')[0])
    return version


def v(version):
    """Convert a version string to a tuple. The tuple can be use to compare
    versions between them.

        >>> from odoorpc.tools import v
        >>> v('7.0')
        [7, 0]
        >>> v('6.1')
        [6, 1]
        >>> v('7.0') < v('6.1')
        False

    :return: the version as tuple
    """
    return [int(x) for x in clean_version(version).split(".")]


def get_encodings(hint_encoding='utf-8'):
    """Used to try different encoding.
    Function copied from Odoo 11.0 (odoo.loglevels.get_encodings).
    This piece of code is licensed under the LGPL-v3 and so it is compatible
    with the LGPL-v3 license of OdooRPC::

        - https://github.com/odoo/odoo/blob/11.0/LICENSE
        - https://github.com/odoo/odoo/blob/11.0/COPYRIGHT
    """
    fallbacks = {
        'latin1': 'latin9',
        'iso-8859-1': 'iso8859-15',
        'cp1252': '1252',
    }
    if hint_encoding:
        yield hint_encoding
        if hint_encoding.lower() in fallbacks:
            yield fallbacks[hint_encoding.lower()]

    # some defaults (also taking care of pure ASCII)
    for charset in ['utf8', 'latin1', 'ascii']:
        if not hint_encoding or (charset.lower() != hint_encoding.lower()):
            yield charset

    from locale import getpreferredencoding

    prefenc = getpreferredencoding()
    if prefenc and prefenc.lower() != 'utf-8':
        yield prefenc
        prefenc = fallbacks.get(prefenc.lower())
        if prefenc:
            yield prefenc
