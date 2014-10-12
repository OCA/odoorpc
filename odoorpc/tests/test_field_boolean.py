# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldBoolean(LoginTestCase):

    def test_field_boolean_read(self):
        self.assertTrue(self.user.active)

    def test_field_boolean_write(self):
        # TODO: split in several unit tests
        partner = self.user.partner_id
        backup = partner.customer
        # True
        partner.customer = True
        data = partner.read(['customer'])[0]
        self.assertEqual(data['customer'], True)
        self.assertEqual(partner.customer, True)
        # False
        partner.customer = False
        data = partner.read(['customer'])[0]
        self.assertEqual(data['customer'], False)
        self.assertEqual(partner.customer, False)
        # None
        partner.customer = None
        data = partner.read(['customer'])[0]
        self.assertEqual(data['customer'], False)
        self.assertEqual(partner.customer, False)
        # Restore original value
        partner.customer = backup
        data = partner.read(['customer'])[0]
        self.assertEqual(data['customer'], backup)
        self.assertEqual(partner.customer, backup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
