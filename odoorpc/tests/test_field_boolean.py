# -*- coding: utf-8 -*-

from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestFieldBoolean(LoginTestCase):
    def test_field_boolean_read(self):
        self.assertTrue(self.user.active)

    def test_field_boolean_write(self):
        # TODO: split in several unit tests
        partner = self.user.partner_id
        if v(self.odoo.version)[0] < 13:
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
        else:
            backup = partner.customer_rank
            # True
            partner.customer_rank = True
            data = partner.read(['customer_rank'])[0]
            self.assertEqual(data['customer_rank'], True)
            self.assertEqual(partner.customer_rank, True)
            # False
            partner.customer_rank = False
            data = partner.read(['customer_rank'])[0]
            self.assertEqual(data['customer_rank'], False)
            self.assertEqual(partner.customer_rank, False)
            # None
            partner.customer_rank = None
            data = partner.read(['customer_rank'])[0]
            self.assertEqual(data['customer_rank'], False)
            self.assertEqual(partner.customer_rank, False)
            # Restore original value
            partner.customer_rank = backup
            data = partner.read(['customer_rank'])[0]
            self.assertEqual(data['customer_rank'], backup)
            self.assertEqual(partner.customer_rank, backup)
