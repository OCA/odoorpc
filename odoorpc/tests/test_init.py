# -*- coding: utf-8 -*-

import sys

import odoorpc
from odoorpc.tests import BaseTestCase

# Python 2
if sys.version_info.major < 3:
    from urllib2 import BaseHandler, URLError, build_opener
# Python >= 3
else:
    from urllib.error import URLError
    from urllib.request import BaseHandler, build_opener


class TestInit(BaseTestCase):
    def test_init1(self):
        # Host + Protocol + Port
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port']
        )
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.host, self.env['host'])
        self.assertEqual(odoo.protocol, self.env['protocol'])
        self.assertEqual(odoo.port, self.env['port'])

    def test_init2(self):
        # Host + Protocol + Port + Timeout
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'], 42
        )
        self.assertIsInstance(odoo, odoorpc.ODOO)
        self.assertIsNotNone(odoo)
        self.assertEqual(odoo.host, self.env['host'])
        self.assertEqual(odoo.protocol, self.env['protocol'])
        self.assertEqual(odoo.port, self.env['port'])
        self.assertEqual(odoo.config['timeout'], 42)

    def test_init_opener(self):
        # Opener
        opener = build_opener(BaseHandler)
        odoo = odoorpc.ODOO(
            self.env['host'],
            self.env['protocol'],
            self.env['port'],
            opener=opener,
        )
        connector = odoo._connector
        self.assertIs(connector._opener, opener)
        self.assertIs(connector._proxy_http._opener, opener)
        self.assertIs(connector._proxy_json._opener, opener)

    def test_init_timeout_none(self):
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'], None
        )
        self.assertIs(odoo.config['timeout'], None)

    def test_init_timeout_float(self):
        odoo = odoorpc.ODOO(
            self.env['host'], self.env['protocol'], self.env['port'], 23.42
        )
        self.assertEqual(odoo.config['timeout'], 23.42)

    def test_init_wrong_protocol(self):
        self.assertRaises(
            ValueError,
            odoorpc.ODOO,
            self.env['host'],
            "wrong",
            self.env['port'],
        )

    def test_init_wrong_port(self):
        self.assertRaises(
            URLError,
            odoorpc.ODOO,
            self.env['host'],
            self.env['protocol'],
            65000,
        )

    def test_init_wrong_port_as_string(self):
        self.assertRaises(
            ValueError,
            odoorpc.ODOO,
            self.env['host'],
            self.env['protocol'],
            "wrong",
        )

    def test_init_wrong_timeout_as_string(self):
        self.assertRaises(
            ValueError,
            odoorpc.ODOO,
            self.env['host'],
            self.env['protocol'],
            self.env['port'],
            "wrong",
        )
