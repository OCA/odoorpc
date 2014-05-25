# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

from oerplib import tools


class TestTools(unittest.TestCase):

    def test_clean_version_numeric(self):
        version = tools.clean_version('6.1')
        self.assertEqual(version, '6.1')

    def test_clean_version_alphanumeric(self):
        version = tools.clean_version('7.0alpha-20121206-000102')
        self.assertEqual(version, '7.0')

    def test_detect_version(self):
        version = tools.detect_version(
            ARGS.server, ARGS.protocol, ARGS.port)
        self.assertIsInstance(version, str)

    def test_v_numeric(self):
        self.assertEqual(tools.v('7.0'), [7, 0])

    def test_v_alphanumeric(self):
        self.assertEqual(tools.v('7.0alpha'), [7, 0])

    def test_v_cmp(self):
        # [(v1, v2, is_inferior), ...]
        versions = [
            ('7.0', '6.1', False), ('6.1', '7.0', True),
            ('7.0alpha', '6.1', False), ('6.1beta', '7.0', True),
            ('6.1beta', '5.0.16', False), ('5.0.16alpha', '6.1', True),
            ('8.0dev-20131102-000101', '7.0-20131014-231047', False),
        ]
        for v1, v2, is_inferior in versions:
            result = tools.v(v1) < tools.v(v2)
            if is_inferior:
                self.assertTrue(result)
            else:
                self.assertFalse(result)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
