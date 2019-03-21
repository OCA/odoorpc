# -*- coding: utf-8 -*-

import socket

from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestTimeout(LoginTestCase):
    def test_increased_timeout(self):
        # Set the timeout
        self.odoo.config['timeout'] = 120
        # Execute a time consuming query: no exception
        report_name = 'web.preview_internalreport'
        if v(self.odoo.version)[0] < 11:
            report_name = 'preview.report'
        self.odoo.report.download(report_name, [1])

    def test_reduced_timeout(self):
        # Set the timeout
        self.odoo.config['timeout'] = 0.005
        # Execute a time consuming query: handle exception
        report_name = 'web.preview_internalreport'
        if v(self.odoo.version)[0] < 11:
            report_name = 'preview.report'
        self.assertRaises(
            socket.timeout, self.odoo.report.download, report_name, [1]
        )
