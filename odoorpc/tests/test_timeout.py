# -*- coding: utf-8 -*-

import base64
import os
import socket

from odoorpc.tests import LoginTestCase


class TestTimeout(LoginTestCase):
    @classmethod
    def setUpClass(cls):
        LoginTestCase.setUpClass()
        dummy_file = os.urandom(1024 ** 2 * 50)  # 50 MB
        b64_data = str(base64.b64encode(dummy_file))
        cls.attachment_values = {"name": "TEST", "datas": b64_data}

    def test_increased_timeout(self):
        # Set the timeout
        self.odoo.config['timeout'] = 120
        # Execute a time consuming query: no exception
        self.odoo.env["ir.attachment"].create(self.attachment_values)

    def test_reduced_timeout(self):
        # partner_model = self.odoo.env["res.partner"]
        attachment_model = self.odoo.env["ir.attachment"]
        # Set the timeout
        self.odoo.config['timeout'] = 0.5
        # Execute a time consuming query: handle exception
        self.assertRaises(
            socket.timeout, attachment_model.create, self.attachment_values
        )

    def tearDown(self):
        self.odoo.config["timetout"] = 120
