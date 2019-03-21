# -*- coding: utf-8 -*-

import re
from doctest import OutputChecker

from sphinx.ext.doctest import SphinxDocTestRunner, setup  # noqa: F401


class Py23OutputChecker(OutputChecker):
    """OutputChecker to ignore unicode literals when checking outputs."""

    def check_output(self, want, got, optionflags):
        if got:
            got = re.sub("u'(.*?)'", "'\\1'", got)
            got = re.sub('u"(.*?)"', '"\\1"', got)
        return OutputChecker.check_output(self, want, got, optionflags)


original_init = SphinxDocTestRunner.__init__


def custom_init(self, checker=None, verbose=None, optionflags=0):
    checker = Py23OutputChecker()
    original_init(self, checker, verbose, optionflags)


SphinxDocTestRunner.__init__ = custom_init
