# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model


class TestFieldReference(LoginTestCase):

    def test_field_reference_read(self):
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

    def test_field_reference_write(self):
        # TODO
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
