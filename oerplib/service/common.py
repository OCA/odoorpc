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
"""Provide the :class:`Common` class to manage the /common RPC service."""

from oerplib import rpc, error


class Common(object):
    """.. versionadded:: 0.6

    The `Common` class represents the ``/common`` RPC service which lets you
    log in on the server, and provides various utility functions.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.common`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> oerp.common
    <oerplib.service.common.Common object at 0xb76266ac>

    .. warning::

        All methods documented below are not strictly implemented in `OERPLib`

        Method calls are purely dynamic, and the following documentation can be
        wrong if the API of the server is changed between versions. Anyway,
        if you know the API proposed by the server for the ``/common`` RPC
        service, it will work.

    .. method:: Common.login(db, login, password)

        >>> oerp.common.login('test_db', 'admin', 'admin_passwd')
        1

        :return: the user's ID or `False`

    .. method:: Common.authenticate(db, login, password, user_agent_env)

        >>> oerp.common.authenticate('test_db', 'admin', 'admin_passwd', {})
        1

        :return: the user's ID or `False`

    .. method:: Common.version()

        >>> oerp.common.version()
        {'protocol_version': 1, 'server_version': '6.1'}

    .. method:: Common.about(extended=False)

        Return information about the server.

        >>> oerp.common.about()
        'See http://openerp.com'

        >>> oerp.common.about(True)
        ['See http://openerp.com', '8.0alpha1']

        :param: extended: if `True` then return version info
        :return: string if extended is `False` else tuple

    .. method:: Common.timezone_get(db, login, password)

        >>> oerp.common.timezone_get('test_db', 'admin', 'admin_passwd')
        'UTC'

    .. method:: Common.get_server_environment()

        >>> print(oerp.common.get_server_environment())
        Environment Information :
        System : Linux-2.6.32-5-686-i686-with-debian-6.0.4
        OS Name : posix
        Distributor ID:	Debian
        Description:	Debian GNU/Linux 6.0.4 (squeeze)
        Release:	6.0.4
        Codename:	squeeze
        Operating System Release : 2.6.32-5-686
        Operating System Version : #1 SMP Mon Mar 26 05:20:33 UTC 2012
        Operating System Architecture : 32bit
        Operating System Locale : fr_FR.UTF8
        Python Version : 2.6.6
        OpenERP-Server Version : 5.0.16
        Last revision No. & ID :

    .. method:: Common.login_message()

        >>> oerp.common.login_message()
        'Welcome'

    .. method:: Common.set_loglevel(loglevel, logger=None)

        >>> oerp.common.set_loglevel('DEBUG')

    .. method:: Common.get_stats()

        >>> print(oerp.common.get_stats())
        OpenERP server: 5 threads
        Servers started
        Net-RPC: running

    .. method:: Common.list_http_services()

        >>> oerp.common.list_http_services()
        []

    .. method:: Common.check_connectivity()

        >>> oerp.common.check_connectivity()
        True

    .. method:: Common.get_os_time()

        >>> oerp.common.get_os_time()
        (0.01, 0.0, 0.0, 0.0, 17873633.129999999)

    .. method:: Common.get_sqlcount()

        >>> oerp.common.get_sqlcount()

    .. method:: Common.get_available_updates(super_admin_password, contract_id, contract_password)

        >>> oerp.common.get_available_updates('super_admin_passwd', 'MY_CONTRACT_ID', 'MY_CONTRACT_PASSWORD')

    .. method:: Common.get_migration_scripts(super_admin_password, contract_id, contract_password)

        >>> oerp.common.get_migration_scripts('super_admin_passwd', 'MY_CONTRACT_ID', 'MY_CONTRACT_PASSWORD')

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def __getattr__(self, method):
        """Provide a dynamic access to a RPC method."""
        def rpc_method(*args):
            """Return the result of the RPC request."""
            try:
                meth = getattr(self._oerp._connector.common, method, False)
                return meth(*args)
            except rpc.error.ConnectorError as exc:
                raise error.RPCError(exc.message, exc.oerp_traceback)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
