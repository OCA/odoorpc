# -*- coding: utf-8 -*-

from odoorpc.tests import BaseTestCase


class TestReqJSON(BaseTestCase):
    def _req_json(self, url):
        data = self.odoo.json(
            url,
            {
                'db': self.env['db'],
                'login': self.env['user'],
                'password': self.env['pwd'],
            },
        )
        self.assertEqual(data['result']['db'], self.env['db'])
        self.assertTrue(data['result']['uid'])
        self.assertEqual(data['result']['username'], self.env['user'])

    def test_req_json_with_leading_slash(self):
        self._req_json('/web/session/authenticate')

    def test_req_json_without_leading_slash(self):
        self._req_json('web/session/authenticate')
