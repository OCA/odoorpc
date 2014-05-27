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
"""Provide the :class:`Common` class to manage the /common RPC service."""

from odoorpc import rpc, error


class Common(object):
    """The `Common` class represents the ``/common`` RPC service which lets you
    log in on the server, and provides various utility functions.

    .. note::
        This service have to be used through the :attr:`odoorpc.OERP.common`
        property.

    >>> import odoorpc
    >>> oerp = odoorpc.OERP('localhost')
    >>> oerp.common
    <odoorpc.service.common.Common object at 0xb76266ac>

    .. warning::

        All methods documented below are not strictly implemented in `OdooRPC`

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
