# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model


class TestFieldMany2one(LoginTestCase):

    def test_field_many2one_read(self):
        User = self.odoo.env['res.users']
        user = User.browse(1)
        company = user.company_id
        self.assertIsInstance(company, Model)
        self.assertEqual(company.id, 1)
        self.assertEqual(company.ids, [1])
        # The environment object can be different as the field could have a
        # custom context defined, so we just check 'db' and 'uid'
        self.assertEqual(company.env.db, user.env.db)
        self.assertEqual(company.env.uid, user.env.uid)
        # Test if empty field returns an empty recordset, and not False
        title = user.title
        self.assertIsInstance(title, Model)
        self.assertEqual(title.id, None)
        self.assertFalse(bool(title))

    def test_field_many2one_write(self):
        self.user.action_id = 1
        self.assertEqual(self.user.action_id.id, 1)
        action = self.odoo.env['ir.actions.actions'].browse(1)
        self.user.action_id = action
        self.assertEqual(self.user.action_id.id, 1)
        # False
        self.user.action_id = False
        self.assertIsInstance(self.user.action_id, Model)
        self.assertEqual(self.user.action_id.id, None)
        self.assertFalse(bool(self.user.action_id))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
