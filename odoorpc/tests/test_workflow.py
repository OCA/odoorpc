# -*- coding: utf-8 -*-


from odoorpc import error, tools
from odoorpc.tests import LoginTestCase


class TestWorkflow(LoginTestCase):
    def setUp(self):
        LoginTestCase.setUp(self)
        if tools.v(self.odoo.version)[0] >= 11:
            # Value doesn't matter for Odoo >= 11, we only test the
            # DeprecationWarning exception for workflow methods
            self.so_id = 1
            return
        self.product_obj = self.odoo.env['product.product']
        self.partner_obj = self.odoo.env['res.partner']
        self.sale_order_obj = self.odoo.env['sale.order']
        self.uom_obj = self.odoo.env['product.uom']
        self.p_id = self.partner_obj.create({'name': "Child 1"})
        prod_vals = {'name': "PRODUCT TEST WORKFLOW"}
        self.product_id = self.product_obj.create(prod_vals)
        sol_vals = {
            'name': "TEST WORKFLOW",
            'product_id': self.product_id,
            'product_uom': self.uom_obj.search([])[0],
        }
        so_vals = {'partner_id': self.p_id, 'order_line': [(0, 0, sol_vals)]}
        self.so_id = self.sale_order_obj.create(so_vals)

    def test_exec_workflow(self):
        if tools.v(self.odoo.version)[0] >= 11:
            self.assertRaises(
                DeprecationWarning,
                self.odoo.exec_workflow,
                'sale.order',
                self.so_id,
                'order_confirm',
            )
            return
        self.odoo.exec_workflow('sale.order', self.so_id, 'order_confirm')

    def test_exec_workflow_wrong_model(self):
        if tools.v(self.odoo.version)[0] >= 11:
            self.assertRaises(
                DeprecationWarning,
                self.odoo.exec_workflow,
                'sale.order2',
                self.so_id,
                'order_confirm',
            )
            return
        self.assertRaises(
            error.RPCError,
            self.odoo.exec_workflow,
            'sale.order2',
            self.so_id,
            'order_confirm',
        )
