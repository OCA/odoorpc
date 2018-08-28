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
"""The `odoorpc` module defines the :class:`ODOO` class.

The :class:`ODOO` class is the entry point to manage `Odoo` servers.
You can use this one to write `Python` programs that performs a variety of
automated jobs that communicate with a `Odoo` server.
"""

__author__ = 'ABF Osiell - Sebastien Alix'
__email__ = 'sebastien.alix@osiell.com'
__licence__ = 'LGPL v3'
__version__ = '0.6.2'

__all__ = ['ODOO', 'error']

from odoorpc.odoo import ODOO
from odoorpc import error

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
