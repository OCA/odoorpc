# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldFloat(LoginTestCase):

    def test_field_float_read(self):
        self.assertEqual(self.user.credit_limit, 0.0)

    def test_field_float_write(self):
        # TODO: split in several unit tests
        partner = self.user.partner_id
        backup = partner.credit_limit
        # False
        partner.credit_limit = False
        data = partner.read(['credit_limit'])[0]
        self.assertEqual(data['credit_limit'], 0.0)
        self.assertEqual(partner.credit_limit, 0.0)
        # None
        partner.credit_limit = None
        data = partner.read(['credit_limit'])[0]
        self.assertEqual(data['credit_limit'], 0.0)
        self.assertEqual(partner.credit_limit, 0.0)
        # 0.0
        partner.credit_limit = 0.0
        data = partner.read(['credit_limit'])[0]
        self.assertEqual(data['credit_limit'], 0.0)
        self.assertEqual(partner.credit_limit, 0.0)
        # 100.0
        partner.credit_limit = 100.0
        data = partner.read(['credit_limit'])[0]
        self.assertEqual(data['credit_limit'], 100.0)
        self.assertEqual(partner.credit_limit, 100.0)
        # Restore original value
        partner.credit_limit = backup
        data = partner.read(['credit_limit'])[0]
        self.assertEqual(data['credit_limit'], backup)
        self.assertEqual(partner.credit_limit, backup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
