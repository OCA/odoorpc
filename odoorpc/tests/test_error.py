# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import sys

from odoorpc.error import RPCError


class TestError(unittest.TestCase):
    def test_rpcerror_unicode_message(self):
        message = u"é"
        exc = RPCError(message)
        str(exc)
        if sys.version_info[0] < 3:
            unicode(exc)  # noqa: F821

    def test_rpcerror_str_message(self):
        message = "é"
        exc = RPCError(message)
        str(exc)
        if sys.version_info[0] < 3:
            unicode(exc)  # noqa: F821
