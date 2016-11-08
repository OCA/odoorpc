# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model
from odoorpc.tools import v


class TestFieldReference(LoginTestCase):

    def test_field_reference_read(self):
        # 8.0 and 9.0
        if v(self.odoo.version) < v('10'):
            Claim = self.odoo.env['crm.claim']
            claim_id = Claim.search([])[0]
            # Test field containing a value
            self.odoo.execute(
                'crm.claim', 'write', [claim_id], {'ref': 'res.partner,1'})
            claim = Claim.browse(claim_id)
            self.assertIsInstance(claim.ref, Model)
            self.assertEqual(claim.ref._name, 'res.partner')
            self.assertEqual(claim.ref.id, 1)
            # Test if empty field returns False (unable to guess the model to use)
            self.odoo.execute(
                'crm.claim', 'write', [claim_id], {'ref': None})
            claim = Claim.browse(claim_id)
            self.assertEqual(claim.ref, False)
        # 10.0
        else:
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

    def test_field_reference_write(self):
        # TODO
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
