# -*- coding: UTF-8 -*-
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
"""This module contains some helper functions used to save and load sessions
in `OERPLib`.
"""
import os
import stat
from ConfigParser import SafeConfigParser

from oerplib import error


def get_all(rc_file='~/.oerplibrc'):
    """Return all session configurations from the `rc_file` file.
    
    >>> import oerplib
    >>> oerplib.tools.session.get_all()
    {'foo': {'protocol': 'xmlrpc', 'user': 'admin', 'timeout': 120, 'database': 'db_name', 'passwd': 'admin', 'type': 'OERP', 'port': 8069, 'server': 'localhost'}}
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    sessions = {}
    for name in conf.sections():
        sessions[name] = {
            'type': conf.get(name, 'type'),
            'server': conf.get(name, 'server'),
            'protocol': conf.get(name, 'protocol'),
            'port': conf.getint(name, 'port'),
            'timeout': conf.getint(name, 'timeout'),
            'user': conf.get(name, 'user'),
            'passwd': conf.get(name, 'passwd'),
            'database': conf.get(name, 'database'),
        }
    return sessions


def get(name, rc_file='~/.oerplibrc'):
    """Return the session configuration identified by `name`
    from the `rc_file` file.

    >>> import oerplib
    >>> oerplib.tools.session.get('foo')
    {'protocol': 'xmlrpc', 'user': 'admin', 'timeout': 120, 'database': 'db_name', 'passwd': 'admin', 'type': 'OERP', 'port': 8069, 'server': 'localhost'}

    :raise: :class:`oerplib.error.Error`
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise error.Error(
            "'{0}' session does not exist".format(name))
    return {
        'type': conf.get(name, 'type'),
        'server': conf.get(name, 'server'),
        'protocol': conf.get(name, 'protocol'),
        'port': conf.getint(name, 'port'),
        'timeout': conf.getint(name, 'timeout'),
        'user': conf.get(name, 'user'),
        'passwd': conf.get(name, 'passwd'),
        'database': conf.get(name, 'database'),
    }


#def list(rc_file='~/.oerplibrc'):
#    """Return a list of all sessions available in the
#    `rc_file` file.
#    """
#    conf = SafeConfigParser()
#    conf.read([os.path.expanduser(rc_file)])
#    # TODO
#    return conf.sections()


def save(name, data, rc_file='~/.oerplibrc'):
    """Save the `data` session configuration under the name `name`
    in the `rc_file` file.

    >>> import oerplib
    >>> oerplib.tools.session.save('foo', {'type': 'OERP', 'server': 'localhost', 'protocol': 'xmlrpc', 'port': 8069, 'timeout': 120, 'user': 'admin', 'passwd': 'admin', 'database': 'db_name'})
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        conf.add_section(name)
    for k, v in data.iteritems():
        conf.set(name, k, str(v))
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        os.chmod(os.path.expanduser(rc_file), stat.S_IREAD | stat.S_IWRITE)
        conf.write(file_)


def remove(name, rc_file='~/.oerplibrc'):
    """Remove the session configuration identified by `name`
    from the `rc_file` file.

    >>> import oerplib
    >>> oerplib.tools.session.remove('foo')

    :raise: :class:`oerplib.error.Error`
    """
    conf = SafeConfigParser()
    conf.read([os.path.expanduser(rc_file)])
    if not conf.has_section(name):
        raise error.Error(
            "'{0}' session does not exist".format(name))
    conf.remove_section(name)
    with open(os.path.expanduser(rc_file), 'wb') as file_:
        conf.write(file_)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
