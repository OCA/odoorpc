# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
import tempfile
import os

from args import ARGS

import odoorpc


class TestSession(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.odoo.login(ARGS.user, ARGS.passwd, ARGS.database)
        self.session_name = ARGS.database
        self.file_path = tempfile.mkstemp(suffix='.cfg', prefix='odoorpc_')[1]

    def tearDown(self):
        os.remove(self.file_path)

    def test_session_odoo_list(self):
        result = odoorpc.OERP.list(rc_file=self.file_path)
        self.assertIsInstance(result, list)
        other_file_path = tempfile.mkstemp()[1]
        result = odoorpc.OERP.list(rc_file=other_file_path)
        self.assertIsInstance(result, list)

    def test_session_odoo_save_and_remove(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        result = odoorpc.OERP.list(rc_file=self.file_path)
        self.assertIn(self.session_name, result)
        odoorpc.OERP.remove(self.session_name, rc_file=self.file_path)

    def test_session_odoo_load(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        odoo = odoorpc.OERP.load(self.session_name, rc_file=self.file_path)
        self.assertIsInstance(odoo, odoorpc.OERP)
        self.assertEqual(self.odoo.server, odoo.server)
        self.assertEqual(self.odoo.port, odoo.port)
        self.assertEqual(self.odoo.database, odoo.database)
        self.assertEqual(self.odoo.protocol, odoo.protocol)
        self.assertEqual(self.odoo.user, odoo.user)
        odoorpc.OERP.remove(self.session_name, rc_file=self.file_path)

    def test_session_tools_get(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        data = {
            'type': self.odoo.__class__.__name__,
            'server': self.odoo.server,
            'protocol': self.odoo.protocol,
            'port': int(self.odoo.port),
            'timeout': self.odoo.config['timeout'],
            'user': self.odoo.user.login,
            'passwd': self.odoo._password,
            'database': self.odoo.database,
        }
        result = odoorpc.tools.session.get(
            self.session_name, rc_file=self.file_path)
        self.assertEqual(data, result)
        odoorpc.OERP.remove(self.session_name, rc_file=self.file_path)

    def test_session_tools_get_all(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        data = {
            self.session_name: {
                'type': self.odoo.__class__.__name__,
                'server': self.odoo.server,
                'protocol': self.odoo.protocol,
                'port': int(self.odoo.port),
                'timeout': self.odoo.config['timeout'],
                'user': self.odoo.user.login,
                'passwd': self.odoo._password,
                'database': self.odoo.database,
            }
        }
        result = odoorpc.tools.session.get_all(rc_file=self.file_path)
        self.assertIn(self.session_name, result)
        self.assertEqual(data, result)
        odoorpc.OERP.remove(self.session_name, rc_file=self.file_path)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
