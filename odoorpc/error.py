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
"""This module contains all exceptions raised by `OdooRPC` when an error
occurred.
"""


class Error(Exception):
    """Base class for exception."""
    def __init__(self, msg, odoo_traceback=False):
        super(Error, self).__init__()
        self.msg = msg
        self.odoo_traceback = odoo_traceback

    def __str__(self):
        return repr(self.msg)


class RPCError(Error):
    """Exception raised for errors related to RPC queries."""
    pass


class LoginError(Error):
    """Exception raised when the login on a server has failed."""
    pass


class InternalError(Error):
    """Exception raised for errors occurring during an internal operation."""
    pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
