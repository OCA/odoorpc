# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib


class TestOSV(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_model(self):
        # Check the result returned
        self.oerp.get('res.users')

    def test_model_method(self):
        # Check the result returned
        model = self.oerp.get('res.users')
        model.name_get(self.user.id)
        self.oerp.get('ir.sequence').get('fake.code')  # Return False

    def test_model_method_without_args(self):
        # Handle exception (execute a 'name_get' with without args)
        model = self.oerp.get('res.users')
        self.assertRaises(
            oerplib.error.RPCError,
            model.name_get)

    def test_model_method_with_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        model = self.oerp.get('res.users')
        self.assertRaises(
            oerplib.error.RPCError,
            model.search,
            False)  # Wrong arg

    def test_model_browse_with_one_id(self):
        # Check the result returned
        model = self.oerp.get('res.users')
        user = model.browse(self.user.id)
        self.assertEqual(user, self.user)

    def test_model_browse_with_ids(self):
        # Iteration
        for result in self.oerp.get('res.users').browse([self.user.id]):
            self.assertEqual(self.user, result)
        user_ids = self.oerp.search('res.users', [])
        for result in self.oerp.get('res.users').browse(user_ids):
            self.assertIsInstance(
                result, oerplib.service.osv.browse.BrowseRecord)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        for result in self.oerp.get('res.users').browse(user_ids, context):
            self.assertIsInstance(
                result, oerplib.service.osv.browse.BrowseRecord)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
