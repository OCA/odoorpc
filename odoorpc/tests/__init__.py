# -*- coding: UTF-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

import os

import odoorpc


class BaseTestCase(unittest.TestCase):
    """Instanciates an ``odoorpc.ODOO`` object, nothing more."""
    def setUp(self):
        try:
            port = int(os.environ.get('ORPC_TEST_PORT', 8069))
        except ValueError:
            raise ValueError("The port must be an integer")
        self.env = {
            'protocol': os.environ.get('ORPC_TEST_PROTOCOL', 'jsonrpc'),
            'host': os.environ.get('ORPC_TEST_HOST', 'localhost'),
            'port': port,
            'db': os.environ.get('ORPC_TEST_DB', 'odoorpc_test'),
            'user': os.environ.get('ORPC_TEST_USER', 'admin'),
            'pwd': os.environ.get('ORPC_TEST_PWD', 'admin'),
            'version': os.environ.get('ORPC_TEST_VERSION', None),
            'super_pwd': os.environ.get('ORPC_TEST_SUPER_PWD', 'admin'),
        }
        self.odoo = odoorpc.ODOO(
            self.env['host'], protocol=self.env['protocol'],
            port=self.env['port'], version=self.env['version'])
        # Create the database
        default_timeout = self.odoo.config['timeout']
        self.odoo.config['timeout'] = 600
        if self.env['db'] not in self.odoo.db.list():
            self.odoo.db.create(
                self.env['super_pwd'], self.env['db'], True)
        self.odoo.config['timeout'] = default_timeout


class LoginTestCase(BaseTestCase):
    """Instanciates an ``odoorpc.ODOO`` object and perform the user login."""
    def setUp(self):
        BaseTestCase.setUp(self)
        default_timeout = self.odoo.config['timeout']
        self.odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        # Install 'sale' + 'crm_claim' on Odoo < 10.0,
        # and 'sale' + 'subscription' on Odoo >= 10.0
        self.odoo.config['timeout'] = 600
        module_obj = self.odoo.env['ir.module.module']
        modules = ['sale', 'crm_claim']
        if self.odoo.version == '10.0':
            modules = ['sale', 'subscription']
        module_ids = module_obj.search([('name', 'in', modules)])
        module_obj.button_immediate_install(module_ids)
        self.odoo.config['timeout'] = default_timeout
        # Get user record and model after the installation of modules
        # to get all available fields (avoiding test failures)
        self.user = self.odoo.env.user
        self.user_obj = self.odoo.env['res.users']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
