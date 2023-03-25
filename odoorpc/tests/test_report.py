# -*- coding: utf-8 -*-

import tempfile

from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestReport(LoginTestCase):
    def test_report_download_pdf(self):
        report_name = 'web.preview_internalreport'
        model = 'res.company'
        if v(self.odoo.version)[0] < 11:
            report_name = 'preview.report'
        ids = self.odoo.env[model].search([])[:20]
        try:
            report = self.odoo.report.download(report_name, ids)
            with tempfile.TemporaryFile(mode='wb', suffix='.pdf') as file_:
                file_.write(report.read())
        except NotImplementedError:
            self.skipTest(
                "Report downloading is not supported in version %s"
                % (self.odoo.version)
            )

    def test_report_download_wrong_report_name(self):
        self.assertRaises(
            ValueError, self.odoo.report.download, 'wrong_report', [1]
        )

    def test_report_list(self):
        res = self.odoo.report.list()
        self.assertIsInstance(res, dict)
        model = 'account.move'
        if v(self.odoo.version)[0] < 13:
            model = 'account.invoice'
        self.assertIn(model, res)
        self.assertTrue(
            any(
                'account.report_invoice' in data['report_name']
                for data in res[model]
            )
        )
