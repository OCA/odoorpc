# -*- coding: utf-8 -*-

import datetime

from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestFieldDate(LoginTestCase):
    def test_field_date_read(self):
        if v(self.odoo.version)[0] >= 19:
            rate = self.odoo.env.ref("base.rateUSD")
            self.assertIsInstance(rate.name, datetime.date)
        else:
            self.assertIsInstance(self.user.login_date, datetime.date)

    def test_field_date_write(self):
        if v(self.odoo.version)[0] < 18:
            partner = self.user.company_id.partner_id
            backup = partner.date
            # False
            partner.date = False
            data = partner.read(["date"])[0]
            self.assertEqual(data["date"], False)
            self.assertEqual(partner.date, False)
            # None
            partner.date = None
            data = partner.read(["date"])[0]
            self.assertEqual(data["date"], False)
            self.assertEqual(partner.date, False)
            # 2012-01-01 (string)
            partner.date = "2012-01-01"
            data = partner.read(["date"])[0]
            self.assertEqual(data["date"], "2012-01-01")
            self.assertEqual(partner.date, datetime.date(2012, 1, 1))
            # 2012-01-01 (date object)
            partner.date = datetime.date(2012, 1, 1)
            data = partner.read(["date"])[0]
            self.assertEqual(data["date"], "2012-01-01")
            self.assertEqual(partner.date, datetime.date(2012, 1, 1))
            # Restore original value
            partner.date = backup
            data = partner.read(["date"])[0]
            self.assertEqual(data["date"], backup and backup.strftime("%Y-%m-%d"))
            self.assertEqual(partner.date, backup)
        else:
            rate = self.odoo.env.ref("base.rateUSD")
            backup = rate.name  # name field is a date
            # NOTE: not testing False and None values
            # 2012-01-01 (string)
            rate.name = "2012-01-01"
            data = self._read(rate._name, rate.ids, ["name"])[0]
            self.assertEqual(data["name"], "2012-01-01")
            self.assertEqual(rate.name, datetime.date(2012, 1, 1))
            # 2012-01-01 (date object)
            rate.name = datetime.date(2012, 1, 1)
            data = self._read(rate._name, rate.ids, ["name"])[0]
            self.assertEqual(data["name"], "2012-01-01")
            self.assertEqual(rate.name, datetime.date(2012, 1, 1))
            # Restore original value
            rate.name = backup
            data = self._read(rate._name, rate.ids, ["name"])[0]
            self.assertEqual(data["name"], backup and backup.strftime("%Y-%m-%d"))
            self.assertEqual(rate.name, backup)
