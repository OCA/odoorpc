# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import odoorpc


class TestOSV(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.odoo.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_model(self):
        # Check the result returned
        self.odoo.get('res.users')

    def test_model_method(self):
        # Check the result returned
        model = self.odoo.get('res.users')
        model.name_get(self.user.id)
        self.odoo.get('ir.sequence').get('fake.code')  # Return False

    def test_model_method_without_args(self):
        # Handle exception (execute a 'name_get' with without args)
        model = self.odoo.get('res.users')
        self.assertRaises(
            odoorpc.error.RPCError,
            model.name_get)

    def test_model_method_with_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        model = self.odoo.get('res.users')
        self.assertRaises(
            odoorpc.error.RPCError,
            model.search,
            False)  # Wrong arg

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
