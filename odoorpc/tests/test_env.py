# -*- coding: UTF-8 -*-

import time

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model
from odoorpc.env import Environment


class TestEnvironment(LoginTestCase):

    def test_env_init(self):
        self.assertIsInstance(self.odoo.env, Environment)

    def test_env_context(self):
        self.assertIn('lang', self.odoo.env.context)
        self.assertIn('tz', self.odoo.env.context)
        self.assertIn('uid', self.odoo.env.context)

    def test_env_lang(self):
        self.assertEqual(self.odoo.env.lang, self.odoo.env.context.get('lang'))

    def test_env_db(self):
        self.assertEqual(self.odoo.env.db, self.env['db'])

    def test_env_user(self):
        self.assertEqual(self.odoo.env.user.login, self.env['user'])

    def test_env_dirty(self):
        self.odoo.config['auto_commit'] = False
        def test_record_garbarge_collected():
            user_ids = self.odoo.env['res.users'].search([('id', '!=', 1)])
            user = self.user_obj.browse(user_ids[0])
            self.assertNotIn(user, self.odoo.env.dirty)
            self.assertNotIn(user, user.env.dirty)
            user.name = "Joe"
            self.assertIn(user, self.odoo.env.dirty)
            self.assertIn(user, user.env.dirty)
        test_record_garbarge_collected()
        # Ensure the record has been garbage collected for the next test
        import gc
        gc.collect()
        self.assertEqual(list(self.odoo.env.dirty), [])

    def test_env_registry(self):
        self.odoo.env['res.partner']
        self.assertIn('res.partner', self.odoo.env.registry)
        del self.odoo.env.registry['res.partner']
        self.assertNotIn('res.partner', self.odoo.env.registry)
        self.user.partner_id
        self.assertIn('res.partner', self.odoo.env.registry)

    def test_env_commit(self):
        # We test with 'auto_commit' deactivated since the commit is implicit
        # by default and sufficiently tested in the 'test_field_*' modules.
        self.odoo.config['auto_commit'] = False
        user_id = self.user_obj.create(
            {'name': "TestCommit", 'login': "test_commit_%s" % time.time()})
        user = self.user_obj.browse(user_id)
        self.assertNotIn(user, self.odoo.env.dirty)
        user.name = "Bob"
        self.assertIn(user, self.odoo.env.dirty)
        self.odoo.env.commit()
        data = user.read(['name'])[0]
        self.assertEqual(data['name'], "Bob")
        self.assertEqual(user.name, "Bob")
        self.assertNotIn(user, self.odoo.env.dirty)

    def test_env_ref(self):
        record = self.odoo.env.ref('base.lang_en')
        self.assertIsInstance(record, Model)
        self.assertEqual(record._name, 'res.lang')
        self.assertEqual(record.code, 'en_US')

    def test_env_contains(self):
        self.assertIn('res.partner', self.odoo.env)
        self.assertNotIn('does.not.exist', self.odoo.env)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
