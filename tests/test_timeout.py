# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest
import socket

from args import ARGS

import oerplib


class TestTimeout(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_reduced_timeout(self):
        ids = self.oerp.search('ir.module.module', [])
        # Set the timeout
        self.oerp.config['timeout'] = 0.1
        # Execute a time consuming query: handle exception
        self.assertRaises(
            socket.timeout,
            self.oerp.write, 'ir.module.module', ids, {})

    def test_increased_timeout(self):
        # Set the timeout
        self.oerp.config['timeout'] = 120
        # Execute a time consuming query: no exception
        ids = self.oerp.search('ir.module.module', [])
        self.oerp.write('ir.module.module', ids, {})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
