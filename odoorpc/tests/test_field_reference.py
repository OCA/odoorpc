# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model


class TestFieldReference(LoginTestCase):

    def test_field_reference_read(self):
        Lead = self.odoo.env['crm.lead']
        lead_id = Lead.search([])[0]
        # Test field containing a value
        self.odoo.execute(
            'crm.lead', 'write', [lead_id], {'ref': 'res.partner,1'})
        lead = Lead.browse(lead_id)
        self.assertIsInstance(lead.ref, Model)
        self.assertEqual(lead.ref._name, 'res.partner')
        self.assertEqual(lead.ref.id, 1)
        # Test if empty field returns False (unable to guess the model to use)
        self.odoo.execute(
            'crm.lead', 'write', [lead_id], {'ref': None})
        lead = Lead.browse(lead_id)
        self.assertEqual(lead.ref, False)

    def test_field_reference_write(self):
        # TODO
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
