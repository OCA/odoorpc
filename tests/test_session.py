# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
import tempfile
import os

from args import ARGS

import oerplib


class TestSession(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.session_name = ARGS.database
        self.file_path = tempfile.mkstemp(suffix='.cfg', prefix='oerplib_')[1]

    def tearDown(self):
        os.remove(self.file_path)

    def test_session_oerp_list(self):
        result = oerplib.OERP.list(rc_file=self.file_path)
        self.assertIsInstance(result, list)
        other_file_path = tempfile.mkstemp()[1]
        result = oerplib.OERP.list(rc_file=other_file_path)
        self.assertIsInstance(result, list)

    def test_session_oerp_save_and_remove(self):
        self.oerp.save(self.session_name, rc_file=self.file_path)
        result = oerplib.OERP.list(rc_file=self.file_path)
        self.assertIn(self.session_name, result)
        oerplib.OERP.remove(self.session_name, rc_file=self.file_path)

    def test_session_oerp_load(self):
        self.oerp.save(self.session_name, rc_file=self.file_path)
        oerp = oerplib.OERP.load(self.session_name, rc_file=self.file_path)
        self.assertIsInstance(oerp, oerplib.OERP)
        self.assertEqual(self.oerp.server, oerp.server)
        self.assertEqual(self.oerp.port, oerp.port)
        self.assertEqual(self.oerp.database, oerp.database)
        self.assertEqual(self.oerp.protocol, oerp.protocol)
        self.assertEqual(self.oerp.user, oerp.user)
        oerplib.OERP.remove(self.session_name, rc_file=self.file_path)

    def test_session_tools_get(self):
        self.oerp.save(self.session_name, rc_file=self.file_path)
        data = {
            'type': self.oerp.__class__.__name__,
            'server': self.oerp.server,
            'protocol': self.oerp.protocol,
            'port': int(self.oerp.port),
            'timeout': self.oerp.config['timeout'],
            'user': self.oerp.user.login,
            'passwd': self.oerp._password,
            'database': self.oerp.database,
        }
        result = oerplib.tools.session.get(
            self.session_name, rc_file=self.file_path)
        self.assertEqual(data, result)
        oerplib.OERP.remove(self.session_name, rc_file=self.file_path)

    def test_session_tools_get_all(self):
        self.oerp.save(self.session_name, rc_file=self.file_path)
        data = {
            self.session_name: {
                'type': self.oerp.__class__.__name__,
                'server': self.oerp.server,
                'protocol': self.oerp.protocol,
                'port': int(self.oerp.port),
                'timeout': self.oerp.config['timeout'],
                'user': self.oerp.user.login,
                'passwd': self.oerp._password,
                'database': self.oerp.database,
            }
        }
        result = oerplib.tools.session.get_all(rc_file=self.file_path)
        self.assertIn(self.session_name, result)
        self.assertEqual(data, result)
        oerplib.OERP.remove(self.session_name, rc_file=self.file_path)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
