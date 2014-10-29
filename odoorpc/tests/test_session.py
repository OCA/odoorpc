# -*- coding: UTF-8 -*-

import tempfile
import os

from odoorpc.tests import LoginTestCase
import odoorpc


class TestSession(LoginTestCase):

    def setUp(self):
        LoginTestCase.setUp(self)
        self.session_name = self.env['db']
        self.file_path = tempfile.mkstemp(suffix='.cfg', prefix='odoorpc_')[1]

    def tearDown(self):
        os.remove(self.file_path)

    def test_session_odoo_list(self):
        result = odoorpc.ODOO.list(rc_file=self.file_path)
        self.assertIsInstance(result, list)
        other_file_path = tempfile.mkstemp()[1]
        result = odoorpc.ODOO.list(rc_file=other_file_path)
        self.assertIsInstance(result, list)

    def test_session_odoo_save_and_remove(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        result = odoorpc.ODOO.list(rc_file=self.file_path)
        self.assertIn(self.session_name, result)
        odoorpc.ODOO.remove(self.session_name, rc_file=self.file_path)

    def test_session_odoo_load(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        odoo = odoorpc.ODOO.load(self.session_name, rc_file=self.file_path)
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertEqual(self.odoo.host, odoo.host)
        self.assertEqual(self.odoo.port, odoo.port)
        self.assertEqual(self.odoo.protocol, odoo.protocol)
        self.assertEqual(self.odoo.env.db, odoo.env.db)
        self.assertEqual(self.odoo.env.uid, odoo.env.uid)
        odoorpc.ODOO.remove(self.session_name, rc_file=self.file_path)

    def test_session_get(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        data = {
            'type': self.odoo.__class__.__name__,
            'host': self.odoo.host,
            'protocol': self.odoo.protocol,
            'port': int(self.odoo.port),
            'timeout': self.odoo.config['timeout'],
            'user': self.odoo._login,
            'passwd': self.odoo._password,
            'database': self.odoo.env.db,
        }
        result = odoorpc.session.get(
            self.session_name, rc_file=self.file_path)
        self.assertEqual(data, result)
        odoorpc.ODOO.remove(self.session_name, rc_file=self.file_path)

    def test_session_get_all(self):
        self.odoo.save(self.session_name, rc_file=self.file_path)
        data = {
            self.session_name: {
                'type': self.odoo.__class__.__name__,
                'host': self.odoo.host,
                'protocol': self.odoo.protocol,
                'port': int(self.odoo.port),
                'timeout': self.odoo.config['timeout'],
                'user': self.odoo._login,
                'passwd': self.odoo._password,
                'database': self.odoo.env.db,
            }
        }
        result = odoorpc.session.get_all(rc_file=self.file_path)
        self.assertIn(self.session_name, result)
        self.assertEqual(data, result)
        odoorpc.ODOO.remove(self.session_name, rc_file=self.file_path)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
