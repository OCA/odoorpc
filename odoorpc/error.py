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
"""This module contains all exceptions raised by `OERPLib` when an error
occurred.
"""


class Error(Exception):
    def __init__(self, message, oerp_traceback=False):
        super(Error, self).__init__()
        self.message = message
        self.oerp_traceback = oerp_traceback

    def __str__(self):
        return "{message}".format(message=self.message)


class RPCError(Error):
    """Exception raised when an error related to a RPC query occurred."""
    pass


class InternalError(Error):
    """Exception raised when an error occurred during an internal operation."""
    pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
