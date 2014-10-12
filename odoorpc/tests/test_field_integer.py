# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldInteger(LoginTestCase):

    def test_field_integer_read(self):
        self.assertIsInstance(self.user.id, int)

    def test_field_integer_write(self):
        cur_obj = self.odoo.env['res.currency']
        cur = cur_obj.browse(1)
        backup = cur.accuracy
        # False
        cur.accuracy = False
        data = cur.read(['accuracy'])[0]
        self.assertEqual(data['accuracy'], 0)
        self.assertEqual(cur.accuracy, 0)
        # None
        cur.accuracy = None
        data = cur.read(['accuracy'])[0]
        self.assertEqual(data['accuracy'], 0)
        self.assertEqual(cur.accuracy, 0)
        # 0
        cur.accuracy = 0
        data = cur.read(['accuracy'])[0]
        self.assertEqual(data['accuracy'], 0)
        self.assertEqual(cur.accuracy, 0)
        # 100
        cur.accuracy = 100
        data = cur.read(['accuracy'])[0]
        self.assertEqual(data['accuracy'], 100)
        self.assertEqual(cur.accuracy, 100)
        # Restore original value
        cur.accuracy = backup
        data = cur.read(['accuracy'])[0]
        self.assertEqual(data['accuracy'], backup)
        self.assertEqual(cur.accuracy, backup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
