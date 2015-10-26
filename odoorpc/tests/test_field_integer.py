# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldInteger(LoginTestCase):

    def test_field_integer_read(self):
        self.assertIsInstance(self.user.id, int)

    def test_field_integer_write(self):
        cron_obj = self.odoo.env['ir.cron']
        cron = cron_obj.browse(cron_obj.search([])[0])
        backup = cron.priority
        # False
        cron.priority = False
        data = cron.read(['priority'])[0]
        self.assertEqual(data['priority'], 0)
        self.assertEqual(cron.priority, 0)
        # None
        cron.priority = None
        data = cron.read(['priority'])[0]
        self.assertEqual(data['priority'], 0)
        self.assertEqual(cron.priority, 0)
        # 0
        cron.priority = 0
        data = cron.read(['priority'])[0]
        self.assertEqual(data['priority'], 0)
        self.assertEqual(cron.priority, 0)
        # 100
        cron.priority = 100
        data = cron.read(['priority'])[0]
        self.assertEqual(data['priority'], 100)
        self.assertEqual(cron.priority, 100)
        # Restore original value
        cron.priority = backup
        data = cron.read(['priority'])[0]
        self.assertEqual(data['priority'], backup)
        self.assertEqual(cron.priority, backup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
