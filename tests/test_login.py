# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import odoorpc
from odoorpc.service import osv


class TestLogin(unittest.TestCase):

    def test_odoo_no_db_login_db(self):
        # OERP no database + login database
        odoo = odoorpc.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = odoo.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(odoo.user, user)
        self.assertEqual(odoo.database, ARGS.database)

    def test_odoo_no_db_login_no_db(self):
        # OERP no database + login no database => Error
        odoo = odoorpc.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.assertRaises(
            odoorpc.error.Error,
            odoo.login, ARGS.user, ARGS.passwd)

    def test_odoo_db_login_no_db(self):
        # OERP database + login no database
        odoo = odoorpc.OERP(
            ARGS.server, ARGS.database, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = odoo.login(ARGS.user, ARGS.passwd)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(odoo.user, user)

    def test_odoo_db_login_db(self):
        # OERP database + login database
        odoo = odoorpc.OERP(
            ARGS.server, ARGS.database, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = odoo.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(odoo.user, user)
        self.assertEqual(odoo.database, ARGS.database)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
