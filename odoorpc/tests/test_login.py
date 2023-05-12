# -*- coding: utf-8 -*-

from contextlib import closing

import odoorpc
from odoorpc.error import InternalError
from odoorpc.models import Model
from odoorpc.tests import BaseTestCase
from odoorpc.tools import v


class TestLogin(BaseTestCase):
    def test_login(self):
        odoo = odoorpc.ODOO(
            self.env['host'],
            protocol=self.env['protocol'],
            port=self.env['port'],
            version=self.env['version'],
        )
        odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        self.assertIsNotNone(odoo.env)
        self.assertIsInstance(odoo.env.user, Model)
        self.assertIn('res.users', odoo.env.registry)
        self.assertEqual(odoo.env.db, self.env['db'])

    def test_login_with_api_key(self):
        if v(self.odoo.version)[0] < 14:
            self.skipTest("API Keys are supported starting from Odoo >= 14")
        odoo = odoorpc.ODOO(
            self.env['host'],
            protocol=self.env['protocol'],
            port=self.env['port'],
            version=self.env['version'],
        )
        odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        odoo.json(
            # Required to use '/web/dataset/call_button' below
            "/web/session/authenticate",
            {
                "db": self.env['db'],
                "login": self.env['user'],
                "password": self.env['pwd'],
            },
        )
        # Generate an API key
        KeyGenerator = odoo.env["res.users.apikeys.description"]
        key_generator_id = KeyGenerator.create({"name": "TEST"})
        data = odoo.json(
            # NOTE Workaround: act like the Odoo web client.
            # Use of '/web/dataset/call_button' instead of '/jsonrpc' to bypass
            # the 'check_identity' check for Odoo >= 16.0.
            "/web/dataset/call_button",
            params={
                "args": [[key_generator_id]],
                "kwargs": {"context": odoo.env.context},
                "method": "make_key",
                "model": "res.users.apikeys.description",
            },
        )
        action = data["result"]
        IdentityCheck = odoo.env["res.users.identitycheck"]
        if action.get("res_model") == IdentityCheck._name:
            check = IdentityCheck.browse(action["res_id"])
            check.password = self.env["pwd"]
            data = odoo.json(
                # NOTE Workaround: act like the Odoo web client.
                # Use of '/web/dataset/call_button' instead of '/jsonrpc' to bypass
                # the 'check_identity' check for Odoo >= 16.0.
                "/web/dataset/call_button",
                params={
                    "args": [[check.id]],
                    "kwargs": {"context": odoo.env.context},
                    "method": "run_check",
                    "model": check._name,
                },
            )
            action = data["result"]
        self.assertEqual(action["res_model"], "res.users.apikeys.show")
        api_key = action["context"]["default_key"]
        # Login with the API key
        odoo.login(self.env['db'], self.env['user'], api_key)
        self.assertIsNotNone(odoo.env)
        self.assertIsInstance(odoo.env.user, Model)
        self.assertIn('res.users', odoo.env.registry)
        self.assertEqual(odoo.env.db, self.env['db'])

    def test_login_no_password(self):
        # login no password => Error
        odoo = odoorpc.ODOO(
            self.env['host'],
            protocol=self.env['protocol'],
            port=self.env['port'],
            version=self.env['version'],
        )
        self.assertRaises(
            odoorpc.error.Error,
            odoo.login,
            self.env['db'],
            self.env['user'],
            False,
        )

    def test_logout(self):
        odoo = odoorpc.ODOO(
            self.env['host'],
            protocol=self.env['protocol'],
            port=self.env['port'],
            version=self.env['version'],
        )
        odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        success = odoo.logout()
        self.assertTrue(success)

    def test_logout_without_login(self):
        odoo = odoorpc.ODOO(
            self.env['host'],
            protocol=self.env['protocol'],
            port=self.env['port'],
            version=self.env['version'],
        )
        success = odoo.logout()
        self.assertFalse(success)

    def test_logout_closing(self):
        odoo = odoorpc.ODOO(
            self.env['host'],
            protocol=self.env['protocol'],
            port=self.env['port'],
            version=self.env['version'],
        )
        odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        with closing(odoo):
            odoo._check_logged_user()
        self.assertRaises(InternalError, odoo._check_logged_user)
