# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
from datetime import datetime

from args import ARGS

import odoorpc


class TestDB(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.databases = []

    def test_db_list(self):
        res = self.odoo.db.list()
        self.assertIsInstance(res, list)

    def test_db_list_lang(self):
        res = self.odoo.db.list_lang()
        self.assertIsInstance(res, list)

    def test_db_dump(self):
        dump = self.odoo.db.dump(ARGS.super_admin_passwd, ARGS.database)
        self.assertIsNotNone(dump)

    def test_db_restore_new_database(self):
        dump = self.odoo.db.dump(ARGS.super_admin_passwd, ARGS.database)
        date = datetime.strftime(datetime.today(), '%Y-%m-%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.odoo.db.restore(ARGS.super_admin_passwd, new_database, dump)
        self.databases.append(new_database)

    def test_db_restore_existing_database(self):
        dump = self.odoo.db.dump(ARGS.super_admin_passwd, ARGS.database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.restore,
            ARGS.super_admin_passwd, ARGS.database, dump)

    def tearDown(self):
        for db in self.databases:
            try:
                self.odoo.db.drop(ARGS.super_admin_passwd, db)
            except:
                pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
