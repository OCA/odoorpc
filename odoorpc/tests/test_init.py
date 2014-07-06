# -*- coding: UTF-8 -*-

import urllib2

from odoorpc.tests import BaseTestCase
import odoorpc


class TestInit(BaseTestCase):

    def test_init1(self):
        # Host + Protocol + Port
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'])
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.host, self.env['host'])
        self.assertEqual(odoo.protocol, self.env['protocol'])
        self.assertEqual(odoo.port, self.env['port'])

    def test_init2(self):
        # Host + Protocol + Port + Timeout
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'], 42)
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.host, self.env['host'])
        self.assertEqual(odoo.protocol, self.env['protocol'])
        self.assertEqual(odoo.port, self.env['port'])
        self.assertEqual(odoo.config['timeout'], 42)

    def test_init_wrong_protocol(self):
        self.assertRaises(
            ValueError,
            odoorpc.ODOO,
            self.env['host'], "wrong", self.env['port'])

    def test_init_wrong_port(self):
        self.assertRaises(
            urllib2.URLError,
            odoorpc.ODOO,
            self.env['host'], self.env['protocol'], 65000)

    def test_init_wrong_port_as_string(self):
        self.assertRaises(
            ValueError,
            odoorpc.ODOO,
            self.env['host'], self.env['protocol'], "wrong")

    def test_init_wrong_timeout_as_string(self):
        self.assertRaises(
            ValueError,
            odoorpc.ODOO,
            self.env['host'], self.env['protocol'], self.env['port'], "wrong")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
