# -*- coding: UTF-8 -*-

from odoorpc.tests import BaseTestCase
import odoorpc


class TestInit(BaseTestCase):

    def test_init1(self):
        # Server + Protocol + Port
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'])
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.server, self.env['host'])
        self.assertEqual(odoo.protocol, self.env['protocol'])
        self.assertEqual(odoo.port, self.env['port'])

    def test_init2(self):
        # Server + Protocol + Port + Timeout
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'], 42)
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.server, self.env['host'])
        self.assertEqual(odoo.protocol, self.env['protocol'])
        self.assertEqual(odoo.port, self.env['port'])
        self.assertEqual(odoo.config['timeout'], 42)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
