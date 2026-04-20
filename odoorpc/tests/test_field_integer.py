# -*- coding: utf-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldInteger(LoginTestCase):
    def test_field_integer_read(self):
        self.assertIsInstance(self.user.id, int)

    def test_field_integer_write(self):
        cron_obj = self.odoo.env["ir.cron"]
        cron_ids = self._search("ir.cron", [], active_test=False)[0]
        cron = cron_obj.browse(cron_ids)
        backup = cron.priority
        # False
        cron.priority = False
        data = self._read("ir.cron", cron.ids, ["priority"])[0]
        self.assertEqual(data["priority"], 0)
        self.assertEqual(cron.priority, 0)
        # None
        cron.priority = None
        data = self._read("ir.cron", cron.ids, ["priority"])[0]
        self.assertEqual(data["priority"], 0)
        self.assertEqual(cron.priority, 0)
        # 0
        cron.priority = 0
        data = self._read("ir.cron", cron.ids, ["priority"])[0]
        self.assertEqual(data["priority"], 0)
        self.assertEqual(cron.priority, 0)
        # 100
        cron.priority = 100
        data = self._read("ir.cron", cron.ids, ["priority"])[0]
        self.assertEqual(data["priority"], 100)
        self.assertEqual(cron.priority, 100)
        # Restore original value
        cron.priority = backup
        data = self._read("ir.cron", cron.ids, ["priority"])[0]
        self.assertEqual(data["priority"], backup)
        self.assertEqual(cron.priority, backup)
