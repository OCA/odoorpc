# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
import numbers
import time

from args import ARGS

import oerplib
from oerplib.tools import v


class TestExecuteKw(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        if v(self.oerp.version) < v('6.1'):
            raise unittest.SkipTest(
                "The targetted OpenERP server does not support the "
                "'execute_kw()' method.")
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    # ------
    # Search
    # ------
    def test_execute_kw_search_with_good_args(self):
        # Check the result returned
        result = self.oerp.execute_kw('res.users', 'search', [[]], {})
        self.assertIsInstance(result, list)
        self.assertIn(self.user.id, result)
        result = self.oerp.execute_kw(
            'res.users', 'search',
            [[('id', '=', self.user.id)]], {'order': 'name'})
        self.assertIn(self.user.id, result)
        self.assertEqual(result[0], self.user.id)

    def test_execute_kw_search_without_args(self):
        # Handle exception (execute a 'search' without args)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'res.users',
            'search')

    def test_execute_kw_search_with_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'res.users',
            'search',
            False, False)   # Wrong args

    def test_execute_kw_search_with_wrong_model(self):
        # Handle exception (execute a 'search' with a wrong model)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'wrong.model',  # Wrong model
            'search',
            [[]], {})

    def test_execute_kw_search_with_wrong_method(self):
        # Handle exception (execute a 'search' with a wrong method)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'res.users',
            'wrong_method',  # Wrong method
            [[]], {})

    # ------
    # Create
    # ------
    def test_execute_kw_create_with_good_args(self):
        login = "%s_%s" % ("foobar", time.time())
        # Check the result returned
        result = self.oerp.execute_kw(
            'res.users', 'create',
            [{'name': login, 'login': login}])
        self.assertIsInstance(result, numbers.Number)
        # Handle exception (create another user with the same login)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'res.users', 'create',
            [{'name': login, 'login': login}])

    def test_execute_kw_create_without_args(self):
        # Handle exception (execute a 'create' without args)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'res.users',
            'create')

    def test_execute_kw_create_with_wrong_args(self):
        # Handle exception (execute a 'create' with wrong args)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.execute_kw,
            'res.users',
            'create',
            True, True)   # Wrong args

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
