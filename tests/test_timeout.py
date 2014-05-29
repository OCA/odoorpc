# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
import socket

from args import ARGS

import odoorpc


class TestTimeout(unittest.TestCase):

    def setUp(self):
        self.odoo = odoorpc.ODOO(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.odoo.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_reduced_timeout(self):
        ids = self.odoo.execute('ir.module.module', 'search', [])
        # Set the timeout
        self.odoo.config['timeout'] = 0.1
        # Execute a time consuming query: handle exception
        self.assertRaises(
            socket.timeout,
            self.odoo.execute, 'ir.module.module', 'write', ids, {})

    def test_increased_timeout(self):
        # Set the timeout
        self.odoo.config['timeout'] = 120
        # Execute a time consuming query: no exception
        ids = self.odoo.execute('ir.module.module', 'search', [])
        self.odoo.execute('ir.module.module', 'write', ids, {})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
