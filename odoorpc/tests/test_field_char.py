# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldChar(LoginTestCase):

    def test_field_char_read(self):
        self.assertEqual(self.user.login, self.env['user'])

    def test_field_char_write(self):
        # TODO: split in several unit tests
        partner = self.user.partner_id
        backup = partner.street
        # "A street"
        partner.street = "A street"
        data = partner.read(['street'])[0]
        self.assertEqual(data['street'], "A street")
        self.assertEqual(partner.street, "A street")
        # False
        partner.street = False
        data = partner.read(['street'])[0]
        self.assertEqual(data['street'], False)
        self.assertEqual(partner.street, False)
        # None
        partner.street = None
        data = partner.read(['street'])[0]
        self.assertEqual(data['street'], False)
        self.assertEqual(partner.street, False)
        # Restore original value
        partner.street = backup
        data = partner.read(['street'])[0]
        self.assertEqual(data['street'], backup)
        self.assertEqual(partner.street, backup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
