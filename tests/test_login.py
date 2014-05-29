# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import odoorpc
from odoorpc.service import osv


class TestLogin(unittest.TestCase):

    def test_login(self):
        odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = odoo.login(ARGS.database, ARGS.user, ARGS.passwd)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(odoo.user, user)
        self.assertEqual(odoo.db, ARGS.database)

    def test_login_no_password(self):
        # login no password => Error
        odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.assertRaises(
            odoorpc.error.Error,
            odoo.login, ARGS.user)

    def test_logout(self):
        odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = odoo.login(ARGS.database, ARGS.user, ARGS.passwd)
        success = odoo.logout()
        self.assertTrue(success)

    def test_logout_without_login(self):
        odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        success = odoo.logout()
        self.assertFalse(success)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
