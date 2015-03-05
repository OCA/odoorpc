# -*- coding: UTF-8 -*-

from odoorpc.tests import BaseTestCase
import odoorpc
from odoorpc.models import Model


class TestLogin(BaseTestCase):

    def test_login(self):
        odoo = odoorpc.ODOO(
            self.env['host'], protocol=self.env['protocol'],
            port=self.env['port'], version=self.env['version'])
        odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        self.assertIsNotNone(odoo.env)
        self.assertIsInstance(odoo.env.user, Model)
        self.assertIn('res.users', odoo.env.registry)
        self.assertEqual(odoo.env.db, self.env['db'])

    def test_login_no_password(self):
        # login no password => Error
        odoo = odoorpc.ODOO(
            self.env['host'], protocol=self.env['protocol'],
            port=self.env['port'], version=self.env['version'])
        self.assertRaises(
            odoorpc.error.Error,
            odoo.login, self.env['db'], self.env['user'], False)

    def test_logout(self):
        odoo = odoorpc.ODOO(
            self.env['host'], protocol=self.env['protocol'],
            port=self.env['port'], version=self.env['version'])
        odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        success = odoo.logout()
        self.assertTrue(success)

    def test_logout_without_login(self):
        odoo = odoorpc.ODOO(
            self.env['host'], protocol=self.env['protocol'],
            port=self.env['port'], version=self.env['version'])
        success = odoo.logout()
        self.assertFalse(success)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
