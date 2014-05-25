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
"""Provide the :class:`Wizard` class in order to access the old-style wizards.
"""

from oerplib import rpc, error


class Wizard(object):
    """.. versionadded:: 0.6

    The `Wizard` class represents the ``/wizard`` RPC service which
    lets you access to the old-style wizards.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.wizard`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> user = oerp.login('admin', 'passwd', 'database')
    >>> oerp.wizard
    <oerplib.service.wizard.Wizard object at 0xb76266ac>

    .. warning::

        All methods documented below are not strictly implemented in `OERPLib`

        Method calls are purely dynamic, and the following documentation can be
        wrong if the API of `OpenERP` is changed between versions. Anyway, if
        you know the API proposed by the server for the ``/wizard`` RPC
        service, it will work.

    .. method:: Wizard.create(wiz_name, datas=None)

        >>> oerp.wizard.create('wiz_name')
        1

        :return: the wizard's instance ID

    .. method:: Wizard.execute(wiz_id, datas, action='init', context=None)

        >>> oerp.wizard.execute(1, {'one_field': "Value"})

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def __getattr__(self, method):
        """Provide a dynamic access to a RPC method."""
        def rpc_method(*args):
            """Return the result of the RPC request."""
            try:
                meth = getattr(self._oerp._connector.wizard, method, False)
                return meth(self._oerp.database, self._oerp.user.id, *args)
            except rpc.error.ConnectorError as exc:
                raise error.RPCError(exc.message, exc.oerp_traceback)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
