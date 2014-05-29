# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import odoorpc
from odoorpc.tools import v


class TestDBDrop(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)

    def test_db_drop_existing_database(self):
        res = self.odoo.db.drop(ARGS.super_admin_passwd, ARGS.database)
        self.assertTrue(res)
        db_list = self.odoo.db.list()
        self.assertNotIn(ARGS.database, db_list)

    def test_db_drop_no_existing_database(self):
        if v(self.odoo.version) >= v('6.1'):
            res = self.odoo.db.drop(ARGS.super_admin_passwd, 'fake_db_name')
            self.assertFalse(res)
        else:
            self.assertRaises(
                odoorpc.error.RPCError,
                self.odoo.db.drop,
                ARGS.super_admin_passwd, 'fake_db_name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
