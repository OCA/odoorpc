# -*- coding: UTF-8 -*-

import numbers
import time

from odoorpc.tests import LoginTestCase
import odoorpc


class TestExecuteKw(LoginTestCase):

    # ------
    # Search
    # ------
    def test_execute_kw_search_with_good_args(self):
        # Check the result returned
        result = self.odoo.execute_kw('res.users', 'search', [[]], {})
        self.assertIsInstance(result, list)
        self.assertIn(self.user.id, result)
        result = self.odoo.execute_kw(
            'res.users', 'search',
            [[('id', '=', self.user.id)]], {'order': 'name'})
        self.assertIn(self.user.id, result)
        self.assertEqual(result[0], self.user.id)

    def test_execute_kw_search_without_args(self):
        # Handle exception (execute a 'search' without args)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'res.users',
            'search')

    def test_execute_kw_search_with_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'res.users',
            'search',
            False, False)   # Wrong args

    def test_execute_kw_search_with_wrong_model(self):
        # Handle exception (execute a 'search' with a wrong model)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'wrong.model',  # Wrong model
            'search',
            [[]], {})

    def test_execute_kw_search_with_wrong_method(self):
        # Handle exception (execute a 'search' with a wrong method)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'res.users',
            'wrong_method',  # Wrong method
            [[]], {})

    # ------
    # Create
    # ------
    def test_execute_kw_create_with_good_args(self):
        login = "%s_%s" % ("foobar", time.time())
        # Check the result returned
        result = self.odoo.execute_kw(
            'res.users', 'create',
            [{'name': login, 'login': login}])
        self.assertIsInstance(result, numbers.Number)
        # Handle exception (create another user with the same login)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'res.users', 'create',
            [{'name': login, 'login': login}])

    def test_execute_kw_create_without_args(self):
        # Handle exception (execute a 'create' without args)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'res.users',
            'create')

    def test_execute_kw_create_with_wrong_args(self):
        # Handle exception (execute a 'create' with wrong args)
        self.assertRaises(
            odoorpc.error.RPCError,
            self.odoo.execute_kw,
            'res.users',
            'create',
            True, True)   # Wrong args

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
