# -*- coding: utf-8 -*-

import tempfile
import unittest
from unittest import mock

from odoorpc.report import Report
from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestReport(LoginTestCase):
    def test_report_download_pdf(self):
        report_name = "web.preview_internalreport"
        model = "res.company"
        if v(self.odoo.version)[0] < 11:
            report_name = "preview.report"
        ids = self.odoo.env[model].search([])[:20]
        try:
            report = self.odoo.report.download(report_name, ids)
            with tempfile.TemporaryFile(mode="wb", suffix=".pdf") as file_:
                file_.write(report.read())
        except NotImplementedError:
            self.skipTest(
                "Report downloading is not supported in version %s"
                % (self.odoo.version)
            )

    def test_report_download_wrong_report_name(self):
        self.assertRaises(ValueError, self.odoo.report.download, "wrong_report", [1])

    def test_report_list(self):
        res = self.odoo.report.list()
        self.assertIsInstance(res, dict)
        model = "account.move"
        if v(self.odoo.version)[0] < 13:
            model = "account.invoice"
        self.assertIn(model, res)
        self.assertTrue(
            any("account.report_invoice" in data["report_name"] for data in res[model])
        )


class TestReportDownloadHTTP(unittest.TestCase):
    """Odoo >= 14.0: the report is fetched from the HTTP controller."""

    def _report(self, odoo, password="admin"):
        odoo._password = password
        odoo._login = "admin"
        odoo.env.db = "db"
        odoo.http.return_value.read.return_value = b"%PDF"
        record = mock.Mock(report_type="qweb-pdf", report_name="web.report 1")
        return Report(odoo), record

    def test_download_http(self):
        odoo = mock.MagicMock()
        report, record = self._report(odoo)
        result = report._download_http(record, [2, 3], {"a": 1}, {"lang": "fr_FR"})
        self.assertEqual(result.read(), b"%PDF")
        odoo.json.assert_called_once_with(
            "/web/session/authenticate",
            {"db": "db", "login": "admin", "password": "admin"},
        )
        url = odoo.http.call_args[0][0]
        self.assertTrue(url.startswith("/report/pdf/web.report%201/2,3?"))
        self.assertIn("options=%7B%22a%22%3A+1%7D", url)
        self.assertIn("context=%7B%22lang%22%3A+%22fr_FR%22%7D", url)

    def test_download_http_single_id_no_params(self):
        odoo = mock.MagicMock()
        report, record = self._report(odoo)
        report._download_http(record, 5, None, None)
        odoo.http.assert_called_once_with("/report/pdf/web.report%201/5")

    def test_download_http_needs_password(self):
        odoo = mock.MagicMock()
        report, record = self._report(odoo, password=None)
        self.assertRaises(
            NotImplementedError, report._download_http, record, [1], None, None
        )
