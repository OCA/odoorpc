# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import odoorpc


class TestDBCreate(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)

    def test_db_create(self):
        if ARGS.database not in self.odoo.db.list():
            res = self.odoo.db.create_database(
                ARGS.super_admin_passwd,
                ARGS.database,
                False,
                'en_US',
                ARGS.passwd)
            self.assertTrue(res)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
