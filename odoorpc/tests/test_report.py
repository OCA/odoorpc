# -*- coding: utf-8 -*-

import tempfile

from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestReport(LoginTestCase):
    def test_report_download_pdf(self):
        model = 'res.company'
        report_name = 'web.preview_internalreport'
        if v(self.odoo.version)[0] < 11:
            report_name = 'preview.report'
        ids = self.odoo.env[model].search([])[:20]
        report = self.odoo.report.download(report_name, ids)
        with tempfile.TemporaryFile(mode='wb', suffix='.pdf') as file_:
            file_.write(report.read())

    def test_report_download_qweb_pdf(self):
        model = 'account.invoice'
        report_name = 'account.report_invoice'
        ids = self.odoo.env[model].search([])[:10]
        report = self.odoo.report.download(report_name, ids)
        with tempfile.TemporaryFile(mode='wb', suffix='.pdf') as file_:
            file_.write(report.read())

    def test_report_download_wrong_report_name(self):
        self.assertRaises(
            ValueError, self.odoo.report.download, 'wrong_report', [1]
        )

    def test_report_list(self):
        res = self.odoo.report.list()
        self.assertIsInstance(res, dict)
        self.assertIn('account.invoice', res)
        self.assertTrue(
            any(
                'account.report_invoice' in data['report_name']
                for data in res['account.invoice']
            )
        )
