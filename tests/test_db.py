# -*- coding: UTF-8 -*-

import unittest
from datetime import datetime
import zipfile
import urllib2

from args import ARGS
import odoorpc


class TestDB(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.databases = []     # Keep databases created during tests

    def test_db_dump(self):
        dump = self.odoo.db.dump(
            ARGS.super_admin_passwd, ARGS.database)
        self.assertIn('dump.sql', zipfile.ZipFile(dump).namelist())

    def test_db_backup_wrong_database(self):
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.backup, ARGS.super_admin_passwd, 'wrong_db')

    def test_db_backup_wrong_password(self):
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.backup, 'wrong_password', ARGS.database)

    def test_db_create(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.odoo.db.create(ARGS.super_admin_passwd, new_database)

    def test_db_create_existing_database(self):
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.create, ARGS.super_admin_passwd, ARGS.database)

    def test_db_create_wrong_password(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.create, 'wrong_password', new_database)

    def test_db_drop(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.odoo.db.duplicate(
            ARGS.super_admin_passwd, ARGS.database, new_database)
        res = self.odoo.db.drop(ARGS.super_admin_passwd, new_database)
        self.assertTrue(res)

    def test_db_drop_wrong_database(self):
        res = self.odoo.db.drop(
            ARGS.super_admin_passwd, 'wrong_database')
        self.assertFalse(res)

    def test_db_drop_wrong_password(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.odoo.db.duplicate(
            ARGS.super_admin_passwd, ARGS.database, new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.drop, 'wrong_password', new_database)

    def test_db_duplicate(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.odoo.db.duplicate(
            ARGS.super_admin_passwd, ARGS.database, new_database)

    def test_db_duplicate_wrong_database(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.duplicate,
            ARGS.super_admin_passwd, 'wrong_database', new_database)

    def test_db_duplicate_wrong_password(self):
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.duplicate,
            'wrong_password', ARGS.database, new_database)

    def test_db_list(self):
        res = self.odoo.db.list()
        self.assertIsInstance(res, list)
        self.assertIn(ARGS.database, res)

    def test_db_restore_new_database(self):
        dump = self.odoo.db.backup(ARGS.super_admin_passwd, ARGS.database)
        date = datetime.strftime(datetime.today(), '%Y-%m-%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.odoo.db.restore(
            ARGS.super_admin_passwd, new_database, dump)

    def test_db_restore_existing_database(self):
        dump = self.odoo.db.backup(ARGS.super_admin_passwd, ARGS.database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.restore,
            ARGS.super_admin_passwd, ARGS.database, dump)

    def test_db_restore_wrong_password(self):
        dump = self.odoo.db.backup(ARGS.super_admin_passwd, ARGS.database)
        date = datetime.strftime(datetime.today(), '%Y%m%d_%Hh%Mm%S')
        new_database = "%s_%s" % (ARGS.database, date)
        self.databases.append(new_database)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.db.restore,
            'wrong_password', new_database, dump)

    def tearDown(self):
        """Clean up databases created during tests."""
        for db in self.databases:
            try:
                self.odoo.db.drop(ARGS.super_admin_passwd, db)
            except:
                pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
