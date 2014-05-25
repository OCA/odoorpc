# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib


class TestDBCreate(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)

    def test_db_create(self):
        if ARGS.database not in self.oerp.db.list():
            res = self.oerp.db.create_and_wait(
                ARGS.super_admin_passwd,
                ARGS.database,
                demo_data=False,
                lang='en_US',
                admin_passwd=ARGS.passwd)
            self.assertIsInstance(res, list)
            self.assertNotEqual(res, list())
            self.assertEqual(res[0]['login'], 'admin')
            self.assertEqual(res[0]['password'], ARGS.passwd)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
