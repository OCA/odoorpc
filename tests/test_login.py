# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib
from oerplib.service import osv


class TestLogin(unittest.TestCase):

    def test_oerp_no_db_login_db(self):
        # OERP no database + login database
        oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = oerp.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(oerp.user, user)
        self.assertEqual(oerp.database, ARGS.database)

    def test_oerp_no_db_login_no_db(self):
        # OERP no database + login no database => Error
        oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.assertRaises(
            oerplib.error.Error,
            oerp.login, ARGS.user, ARGS.passwd)

    def test_oerp_db_login_no_db(self):
        # OERP database + login no database
        oerp = oerplib.OERP(
            ARGS.server, ARGS.database, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = oerp.login(ARGS.user, ARGS.passwd)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(oerp.user, user)

    def test_oerp_db_login_db(self):
        # OERP database + login database
        oerp = oerplib.OERP(
            ARGS.server, ARGS.database, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        user = oerp.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, osv.BrowseRecord)
        self.assertEqual(oerp.user, user)
        self.assertEqual(oerp.database, ARGS.database)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
