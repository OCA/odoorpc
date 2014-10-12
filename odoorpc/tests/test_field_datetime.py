# -*- coding: UTF-8 -*-

import datetime

from odoorpc.tests import LoginTestCase


class TestFieldDatetime(LoginTestCase):

    def test_field_datetime_read(self):
        SaleOrder = self.odoo.env['sale.order']
        order_id = SaleOrder.search([('date_order', '!=', False)], limit=1)
        order = SaleOrder.browse(order_id)
        self.assertIsInstance(order.date_order, datetime.datetime)

    def test_field_datetime_write(self):
        # TODO
        # No common model found in every versions of OpenERP with a
        # fields.datetime writable
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
