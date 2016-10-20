# -*- coding: UTF-8 -*-

from datetime import datetime
import zipfile

from odoorpc.tests import BaseTestCase
import odoorpc


class TestDB(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.odoo.logout()
        self.databases = []     # Keep databases created during tests

    def test_db_dump(self):
        dump = self.odoo.db.dump(self.env['super_pwd'], self.env['db'])
        self.assertIn('dump.sql', zipfile.ZipFile(dump).namelist())

    def test_db_dump_wrong_database(self):
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.dump, self.env['super_pwd'], 'wrong_db')

    def test_db_dump_wrong_password(self):
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.dump, 'wrong_password', self.env['db'])

    def test_db_create(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.odoo.db.create(self.env['super_pwd'], new_database)

    def test_db_create_existing_database(self):
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.create, self.env['super_pwd'], self.env['db'])

    def test_db_create_wrong_password(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.create, 'wrong_password', new_database)

    def test_db_drop(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.odoo.db.duplicate(
            self.env['super_pwd'], self.env['db'], new_database)
        res = self.odoo.db.drop(self.env['super_pwd'], new_database)
        self.assertTrue(res)

    def test_db_drop_wrong_database(self):
        res = self.odoo.db.drop(self.env['super_pwd'], 'wrong_database')
        self.assertFalse(res)

    def test_db_drop_wrong_password(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.odoo.db.duplicate(
            self.env['super_pwd'], self.env['db'], new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.drop, 'wrong_password', new_database)

    def test_db_duplicate(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.odoo.db.duplicate(
            self.env['super_pwd'], self.env['db'], new_database)

    def test_db_duplicate_wrong_database(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.duplicate,
            self.env['super_pwd'], 'wrong_database', new_database)

    def test_db_duplicate_wrong_password(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.duplicate,
            'wrong_password', self.env['db'], new_database)

    def test_db_list(self):
        res = self.odoo.db.list()
        self.assertIsInstance(res, list)
        self.assertIn(self.env['db'], res)

    def test_db_restore_new_database(self):
        dump = self.odoo.db.dump(self.env['super_pwd'], self.env['db'])
        date = datetime.strftime(datetime.today(), '%Y-%m-%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.odoo.db.restore(
            self.env['super_pwd'], new_database, dump)

    def test_db_restore_existing_database(self):
        dump = self.odoo.db.dump(self.env['super_pwd'], self.env['db'])
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.restore,
            self.env['super_pwd'], self.env['db'], dump)

    def test_db_restore_wrong_password(self):
        dump = self.odoo.db.dump(self.env['super_pwd'], self.env['db'])
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (self.env['db'], date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.restore,
            'wrong_password', new_database, dump)

    def tearDown(self):
        """Clean up databases created during tests."""
        for db in self.databases:
            try:
                self.odoo.db.drop(self.env['super_pwd'], db)
            except:
                pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
