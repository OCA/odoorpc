# -*- coding: UTF-8 -*-

import socket

from odoorpc.tests import LoginTestCase


class TestTimeout(LoginTestCase):

    def test_increased_timeout(self):
        # Set the timeout
        self.odoo.config['timeout'] = 120
        # Execute a time consuming query: no exception
        self.odoo.report.download('preview.report', [1])

    def test_reduced_timeout(self):
        # Set the timeout
        self.odoo.config['timeout'] = 0.005
        # Execute a time consuming query: handle exception
        self.assertRaises(
            socket.timeout,
            self.odoo.report.download, 'preview.report', [1])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
