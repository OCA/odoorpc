# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib
from oerplib.tools import v


class TestDBDrop(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)

    def test_db_drop_existing_database(self):
        res = self.oerp.db.drop(ARGS.super_admin_passwd, ARGS.database)
        self.assertTrue(res)
        db_list = self.oerp.db.list()
        self.assertNotIn(ARGS.database, db_list)

    def test_db_drop_no_existing_database(self):
        if v(self.oerp.version) >= v('6.1'):
            res = self.oerp.db.drop(ARGS.super_admin_passwd, 'fake_db_name')
            self.assertFalse(res)
        else:
            self.assertRaises(
                oerplib.error.RPCError,
                self.oerp.db.drop,
                ARGS.super_admin_passwd, 'fake_db_name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
