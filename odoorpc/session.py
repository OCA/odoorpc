# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""This module contains some helper functions used to save and load sessions
in `OdooRPC`.
"""
import os
import stat
import sys

# Python 2
if sys.version_info[0] < 3:
    from ConfigParser import SafeConfigParser as ConfigParser
# Python >= 3
else:
    from configparser import ConfigParser


def get_all(rc_file='~/.odoorpcrc'):
    """Return all session configurations from the `rc_file` file.

    >>> import odoorpc
    >>> from pprint import pprint as pp
    >>> pp(odoorpc.session.get_all())     # doctest: +SKIP
    {'foo': {'database': 'db_name',
             'host': 'localhost',
             'passwd': 'password',
             'port': 8069,
             'protocol': 'jsonrpc',
             'timeout': 120,
             'type': 'ODOO',
             'user': 'admin'},
     ...}

    .. doctest::
        :hide:

        >>> import odoorpc
        >>> session = '%s_session' % DB
        >>> odoo.save(session)
        >>> data = odoorpc.session.get_all()
        >>> data[session]['host'] == HOST
        True
        >>> data[session]['protocol'] == PROTOCOL
        True
        >>> data[session]['port'] == int(PORT)
        True
        >>> data[session]['database'] == DB
        True
        >>> data[session]['user'] == USER
        True
        >>> data[session]['passwd'] == PWD
        True
        >>> data[session]['type'] == 'ODOO'
        True
    """
    conf = ConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    sessions = {}
    for name in conf.sections():
        sessions[name] = {
            'type': conf.get(name, 'type'),
            'host': conf.get(name, 'host'),
            'protocol': conf.get(name, 'protocol'),
            'port': conf.getint(name, 'port'),
            'timeout': conf.getfloat(name, 'timeout'),
            'user': conf.get(name, 'user'),
            'passwd': conf.get(name, 'passwd'),
            'database': conf.get(name, 'database'),
        }
    return sessions


def get(name, rc_file='~/.odoorpcrc'):
    """Return the session configuration identified by `name`
    from the `rc_file` file.

    >>> import odoorpc
    >>> from pprint import pprint as pp
    >>> pp(odoorpc.session.get('foo'))    # doctest: +SKIP
    {'database': 'db_name',
     'host': 'localhost',
     'passwd': 'password',
     'port': 8069,
     'protocol': 'jsonrpc',
     'timeout': 120,
     'type': 'ODOO',
     'user': 'admin'}

    .. doctest::
        :hide:

        >>> import odoorpc
        >>> session = '%s_session' % DB
        >>> odoo.save(session)
        >>> data = odoorpc.session.get(session)
        >>> data['host'] == HOST
        True
        >>> data['protocol'] == PROTOCOL
        True
        >>> data['port'] == int(PORT)
        True
        >>> data['database'] == DB
        True
        >>> data['user'] == USER
        True
        >>> data['passwd'] == PWD
        True
        >>> data['type'] == 'ODOO'
        True

    :raise: `ValueError` (wrong session name)
    """
    conf = ConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise ValueError(
            "'{}' session does not exist in {}".format(name, rc_file)
        )
    return {
        'type': conf.get(name, 'type'),
        'host': conf.get(name, 'host'),
        'protocol': conf.get(name, 'protocol'),
        'port': conf.getint(name, 'port'),
        'timeout': conf.getfloat(name, 'timeout'),
        'user': conf.get(name, 'user'),
        'passwd': conf.get(name, 'passwd'),
        'database': conf.get(name, 'database'),
    }


def save(name, data, rc_file='~/.odoorpcrc'):
    """Save the `data` session configuration under the name `name`
    in the `rc_file` file.

    >>> import odoorpc
    >>> odoorpc.session.save(
    ...     'foo',
    ...     {'type': 'ODOO', 'host': 'localhost', 'protocol': 'jsonrpc',
    ...      'port': 8069, 'timeout': 120, 'database': 'db_name'
    ...      'user': 'admin', 'passwd': 'password'})    # doctest: +SKIP

    .. doctest::
        :hide:

        >>> import odoorpc
        >>> session = '%s_session' % DB
        >>> odoorpc.session.save(
        ...     session,
        ...     {'type': 'ODOO', 'host': HOST, 'protocol': PROTOCOL,
        ...      'port': PORT, 'timeout': 120, 'database': DB,
        ...      'user': USER, 'passwd': PWD})
    """
    conf = ConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        conf.add_section(name)
    for key in data:
        value = data[key]
        conf.set(name, key, str(value))
    with open(os.path.expanduser(rc_file), 'w') as file_:
        os.chmod(os.path.expanduser(rc_file), stat.S_IREAD | stat.S_IWRITE)
        conf.write(file_)


def remove(name, rc_file='~/.odoorpcrc'):
    """Remove the session configuration identified by `name`
    from the `rc_file` file.

    >>> import odoorpc
    >>> odoorpc.session.remove('foo')     # doctest: +SKIP

    .. doctest::
        :hide:

        >>> import odoorpc
        >>> session = '%s_session' % DB
        >>> odoorpc.session.remove(session)

    :raise: `ValueError` (wrong session name)
    """
    conf = ConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise ValueError(
            "'{}' session does not exist in {}".format(name, rc_file)
        )
    conf.remove_section(name)
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        conf.write(file_)
