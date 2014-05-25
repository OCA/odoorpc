# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib


class TestInit(unittest.TestCase):

    def test_init1(self):
        # Server + Database + Protocol + Port
        oerp = oerplib.OERP(ARGS.server, ARGS.database,
                            ARGS.protocol, ARGS.port)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertIsNotNone(oerp)
        self.assertEqual(oerp.server, ARGS.server)
        self.assertEqual(oerp.database, ARGS.database)
        self.assertEqual(oerp.protocol, ARGS.protocol)
        self.assertEqual(oerp.port, ARGS.port)

    def test_init2(self):
        # Server + Database + Protocol + Port + Timeout
        oerp = oerplib.OERP(ARGS.server, ARGS.database,
                            ARGS.protocol, ARGS.port, 42)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertIsNotNone(oerp)
        self.assertEqual(oerp.server, ARGS.server)
        self.assertEqual(oerp.database, ARGS.database)
        self.assertEqual(oerp.protocol, ARGS.protocol)
        self.assertEqual(oerp.port, ARGS.port)
        self.assertEqual(oerp.config['timeout'], 42)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
