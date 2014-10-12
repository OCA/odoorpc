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
"""This module contains some helper functions used to save and load sessions
in `OdooRPC`.
"""
import os
import stat
import sys
# Python 2
if sys.version_info.major < 3:
    from ConfigParser import SafeConfigParser as ConfigParser
# Python >= 3
else:
    from configparser import ConfigParser


def get_all(rc_file='~/.odoorpcrc'):
    """Return all session configurations from the `rc_file` file.

    >>> import odoorpc
    >>> odoorpc.tools.session.get_all()
    {'foo': {'protocol': 'jsonrpc', 'user': 'admin', 'timeout': 120, 'database': 'db_name', 'passwd': 'admin', 'type': 'ODOO', 'port': 8069, 'host': 'localhost'}}
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
            'timeout': conf.getint(name, 'timeout'),
            'user': conf.get(name, 'user'),
            'passwd': conf.get(name, 'passwd'),
            'database': conf.get(name, 'database'),
        }
    return sessions


def get(name, rc_file='~/.odoorpcrc'):
    """Return the session configuration identified by `name`
    from the `rc_file` file.

    >>> import odoorpc
    >>> odoorpc.tools.session.get('foo')
    {'protocol': 'jsonrpc', 'user': 'admin', 'timeout': 120, 'database': 'db_name', 'passwd': 'admin', 'type': 'ODOO', 'port': 8069, 'host': 'localhost'}

    :raise: `ValueError` (wrong session name)
    """
    conf = ConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise ValueError(
            "'%s' session does not exist in %s" % (name, rc_file))
    return {
        'type': conf.get(name, 'type'),
        'host': conf.get(name, 'host'),
        'protocol': conf.get(name, 'protocol'),
        'port': conf.getint(name, 'port'),
        'timeout': conf.getint(name, 'timeout'),
        'user': conf.get(name, 'user'),
        'passwd': conf.get(name, 'passwd'),
        'database': conf.get(name, 'database'),
    }


def save(name, data, rc_file='~/.odoorpcrc'):
    """Save the `data` session configuration under the name `name`
    in the `rc_file` file.

    >>> import odoorpc
    >>> odoorpc.tools.session.save(
    ...     'foo',
    ...     {'type': 'ODOO', 'host': 'localhost', 'protocol': 'jsonrpc',
    ...      'port': 8069, 'timeout': 120, 'user': 'admin', 'passwd': 'admin',
    ...      'database': 'db_name'})
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
    >>> odoorpc.tools.session.remove('foo')

    :raise: `ValueError` (wrong session name)
    """
    conf = ConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise ValueError(
            "'%s' session does not exist in %s" % (name, rc_file))
    conf.remove_section(name)
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        conf.write(file_)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
