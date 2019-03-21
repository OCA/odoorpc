# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)


class ConnectorError(BaseException):
    """Exception raised by the ``odoorpc.rpc`` package."""

    def __init__(self, message, odoo_traceback=None):
        self.message = message
        self.odoo_traceback = odoo_traceback
