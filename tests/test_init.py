# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import odoorpc


class TestInit(unittest.TestCase):

    def test_init1(self):
        # Server + Protocol + Port
        odoo = odoorpc.ODOO(ARGS.server, ARGS.protocol, ARGS.port)
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.server, ARGS.server)
        self.assertEqual(odoo.protocol, ARGS.protocol)
        self.assertEqual(odoo.port, ARGS.port)

    def test_init2(self):
        # Server + Protocol + Port + Timeout
        odoo = odoorpc.ODOO(ARGS.server, ARGS.protocol, ARGS.port, 42)
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.server, ARGS.server)
        self.assertEqual(odoo.protocol, ARGS.protocol)
        self.assertEqual(odoo.port, ARGS.port)
        self.assertEqual(odoo.config['timeout'], 42)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
