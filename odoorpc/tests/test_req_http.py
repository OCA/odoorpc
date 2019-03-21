# -*- coding: utf-8 -*-

from odoorpc.tests import BaseTestCase


class TestReqHTTP(BaseTestCase):
    def _req_http(self, url):
        response = self.odoo.http(url)
        binary_data = response.read()
        self.assertTrue(binary_data)

    def test_req_http_with_leading_slash(self):
        self._req_http('/web/binary/company_logo')

    def test_req_http_without_leading_slash(self):
        self._req_http('web/binary/company_logo')
