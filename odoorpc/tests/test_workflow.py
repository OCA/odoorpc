# -*- coding: UTF-8 -*-


from odoorpc.tests import LoginTestCase
from odoorpc import error


class TestWorkflow(LoginTestCase):

    def setUp(self):
        LoginTestCase.setUp(self)
        self.product_obj = self.odoo.env['product.product']
        self.partner_obj = self.odoo.env['res.partner']
        self.sale_order_obj = self.odoo.env['sale.order']
        self.uom_obj = self.odoo.env['product.uom']
        self.p_id = self.partner_obj.create({'name': "Child 1"})
        prod_vals = {
            'name': "PRODUCT TEST WORKFLOW",
        }
        self.product_id = self.product_obj.create(prod_vals)
        sol_vals = {
            'name': "TEST WORKFLOW",
            'product_id': self.product_id,
            'product_uom': self.uom_obj.search([])[0],
        }
        so_vals = {
            'partner_id': self.p_id,
            'order_line': [(0, 0, sol_vals)],
        }
        self.so_id = self.sale_order_obj.create(so_vals)

    def test_exec_workflow(self):
        self.odoo.exec_workflow('sale.order', self.so_id, 'order_confirm')

    def test_exec_workflow_wrong_model(self):
        self.assertRaises(
            error.RPCError,
            self.odoo.exec_workflow,
            'sale.order2', self.so_id, 'order_confirm')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
