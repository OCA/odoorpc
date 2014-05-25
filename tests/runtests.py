#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

from test_tools import TestTools
from test_init import TestInit
from test_login import TestLogin
from test_db_create import TestDBCreate
from test_db import TestDB
from test_db_drop import TestDBDrop
from test_execute import TestExecute
from test_execute_kw import TestExecuteKw
from test_browse import TestBrowse
from test_osv import TestOSV
from test_timeout import TestTimeout
from test_session import TestSession
from test_inspect import TestInspect

from oerplib.tools import v

if __name__ == '__main__':
    suite = unittest.TestSuite()

    #---------------
    #- First Tests -
    #---------------

    # 1) Test oerplib.tools
    loader = unittest.TestLoader().loadTestsFromTestCase(TestTools)
    suite.addTest(loader)

    # 2) Test OERP.__init__
    loader = unittest.TestLoader().loadTestsFromTestCase(TestInit)
    suite.addTest(loader)
    # 3) Test OERP.db (create the database)
    if ARGS.create_db:
        loader = unittest.TestLoader().loadTestsFromTestCase(TestDBCreate)
        suite.addTest(loader)
    else:
        print("-- TestDBCreate skipped --")
    # 4) Test OERP.login
    loader = unittest.TestLoader().loadTestsFromTestCase(TestLogin)
    suite.addTest(loader)

    #---------
    #- Tests -
    #---------

    # Test OERP.db
    loader = unittest.TestLoader().loadTestsFromTestCase(TestDB)
    suite.addTest(loader)

    # Test OERP.execute and OERP.execute_kw
    loader = unittest.TestLoader().loadTestsFromTestCase(TestExecute)
    suite.addTest(loader)
    loader = unittest.TestLoader().loadTestsFromTestCase(TestExecuteKw)
    suite.addTest(loader)

    # Test OERP.browse
    loader = unittest.TestLoader().loadTestsFromTestCase(TestBrowse)
    suite.addTest(loader)

    # Test OERP.get
    loader = unittest.TestLoader().loadTestsFromTestCase(TestOSV)
    suite.addTest(loader)

    # Test socket timeout
    loader = unittest.TestLoader().loadTestsFromTestCase(TestTimeout)
    suite.addTest(loader)

    # Test session management
    loader = unittest.TestLoader().loadTestsFromTestCase(TestSession)
    suite.addTest(loader)

    # Test inspect service
    loader = unittest.TestLoader().loadTestsFromTestCase(TestInspect)
    suite.addTest(loader)

    #---------------
    #- Final Tests -
    #---------------

    # Test OERP.db (drop the database)
    if ARGS.create_db and ARGS.drop_db:
        loader = unittest.TestLoader().loadTestsFromTestCase(TestDBDrop)
        suite.addTest(loader)
    else:
        print("-- TestDBDrop skipped --")

    # Run all tests
    if ARGS.test_xmlrpc:
        print("-- RUN (XMLRPC) --")
        ARGS.protocol = 'xmlrpc'
        ARGS.port = int(ARGS.xmlrpc_port)
        unittest.TextTestRunner(verbosity=ARGS.verbosity).run(suite)
    if ARGS.test_netrpc:
        print("-- RUN (NETRPC) --")
        ARGS.protocol = 'netrpc'
        ARGS.port = int(ARGS.netrpc_port)
        unittest.TextTestRunner(verbosity=ARGS.verbosity).run(suite)
    if not ARGS.test_xmlrpc and not ARGS.test_netrpc:
        print("-- NO TEST --")
        print("Please use '--test_xmlrpc' and/or '--test_netrpc' option.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
