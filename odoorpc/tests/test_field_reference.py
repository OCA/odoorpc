# -*- coding: utf-8 -*-

from odoorpc.models import Model
from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestFieldReference(LoginTestCase):
    def test_field_reference_read(self):
        # 8.0 and 9.0
        if v(self.odoo.version) < v('10'):
            Claim = self.odoo.env['crm.claim']
            claim_id = Claim.search([])[0]
            # Test field containing a value
            self.odoo.execute(
                'crm.claim', 'write', [claim_id], {'ref': 'res.partner,1'}
            )
            claim = Claim.browse(claim_id)
            self.assertIsInstance(claim.ref, Model)
            self.assertEqual(claim.ref._name, 'res.partner')
            self.assertEqual(claim.ref.id, 1)
            # Test if empty field returns False (unable to guess the model to use)
            self.odoo.execute('crm.claim', 'write', [claim_id], {'ref': None})
            claim = Claim.browse(claim_id)
            self.assertEqual(claim.ref, False)
        # 10.0
        elif v(self.odoo.version) < v('11'):
            Subscription = self.odoo.env['subscription.subscription']
            fields_list = list(Subscription.fields_get([]))
            vals = Subscription.default_get(fields_list)
            vals['name'] = "ODOORPC TEST (fields.Reference)"
            vals['doc_source'] = 'res.partner,1'
            subscription_id = Subscription.create(vals)
            # Test field containing a value
            subscription = Subscription.browse(subscription_id)
            self.assertIsInstance(subscription.doc_source, Model)
            self.assertEqual(subscription.doc_source._name, 'res.partner')
            self.assertEqual(subscription.doc_source.id, 1)
        # 11.0
        else:
            Menu = self.odoo.env['ir.ui.menu']
            fields_list = list(Menu.fields_get([]))
            vals = Menu.default_get(fields_list)
            vals['name'] = "ODOORPC TEST (fields.Reference)"
            action = self.odoo.env.ref('base.action_partner_form')
            vals['action'] = '{},{}'.format(action._name, action.id)
            menu_id = Menu.create(vals)
            # Test field containing a value
            menu = Menu.browse(menu_id)
            self.assertIsInstance(menu.action, Model)
            self.assertEqual(menu.action._name, action._name)
            self.assertEqual(menu.action.id, action.id)

    def test_field_reference_write(self):
        # TODO
        pass
