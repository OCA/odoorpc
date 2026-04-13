# -*- coding: utf-8 -*-

import base64
import logging
import os

from odoorpc.tests import LoginTestCase
from odoorpc.rpc.jsonrpclib import Secret, Bloat


class TestLogging(LoginTestCase):
    @classmethod
    def setUpClass(cls):
        LoginTestCase.setUpClass()
        dummy_file = os.urandom(1024)
        b64_data = str(base64.b64encode(dummy_file))
        cls.attachment_values = {"name": "TEST", "datas": Bloat(b64_data)}

    def test_hidden_parameters_in_logs(self):
        # Expected log output:
        # DEBUG:odoorpc.rpc.jsonrpclib:(JSON,send) http://localhost:8069/jsonrpc {'jsonrpc': '2.0', 'method': 'call', 'params': {'service': 'object', 'method': 'execute_kw', 'args': ['odoorpc_test', 2, '**********', 'ir.attachment', 'create', ({'name': 'TEST', 'datas': '<...>'},), {'context': {'lang': 'en_US', 'tz': 'Europe/Brussels', 'uid': 2}}]}, 'id': 156322240}
        logger = logging.getLogger("odoorpc")
        logger.setLevel(logging.DEBUG)
        with self.assertLogs("odoorpc", level="DEBUG") as logs:
            self.odoo.env["ir.attachment"].create(self.attachment_values)
            # Password and b64 value should be hidden in logs
            hidden_password = (
                f"'{self.odoo.env.db}', {self.odoo.env.uid}, '{Secret.MASK}', "
                "'ir.attachment', 'create'"
            )
            self.assertTrue(any(hidden_password in log for log in logs.output))
            self.assertFalse(any(self.odoo._password in log for log in logs.output))
            hidden_bloat = f"'datas': '{Bloat.MASK}'"
            self.assertTrue(any(hidden_bloat in log for log in logs.output))
            self.assertFalse(
                any(self.attachment_values["datas"] in log for log in logs.output)
            )
