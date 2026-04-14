# -*- coding: utf-8 -*-

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
        data = self._read("res.partner", partner.ids, ["credit_limit"])[0]
        self.assertEqual(data["credit_limit"], 0.0)
        self.assertEqual(partner.credit_limit, 0.0)
        # None
        partner.credit_limit = None
        data = self._read("res.partner", partner.ids, ["credit_limit"])[0]
        self.assertEqual(data["credit_limit"], 0.0)
        self.assertEqual(partner.credit_limit, 0.0)
        # 0.0
        partner.credit_limit = 0.0
        data = self._read("res.partner", partner.ids, ["credit_limit"])[0]
        self.assertEqual(data["credit_limit"], 0.0)
        self.assertEqual(partner.credit_limit, 0.0)
        # 100.0
        partner.credit_limit = 100.0
        data = self._read("res.partner", partner.ids, ["credit_limit"])[0]
        self.assertEqual(data["credit_limit"], 100.0)
        self.assertEqual(partner.credit_limit, 100.0)
        # Restore original value
        partner.credit_limit = backup
        data = self._read("res.partner", partner.ids, ["credit_limit"])[0]
        self.assertEqual(data["credit_limit"], backup)
        self.assertEqual(partner.credit_limit, backup)
