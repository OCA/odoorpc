# -*- coding: UTF-8 -*-

import sys

from odoorpc.tests import LoginTestCase

# Python 2
if sys.version_info.major < 3:
    def is_string(arg):
        return isinstance(arg, str) or isinstance(arg, unicode)
# Python >= 3
else:
    def is_string(arg):
        return isinstance(arg, str)


class TestFieldText(LoginTestCase):

    def test_field_text_read(self):
        # Test empty field
        self.assertFalse(self.user.comment)
        # Test field containing a value
        Module = self.odoo.env['ir.module.module']
        sale_id = Module.search([('name', '=', 'sale')])
        sale_mod = Module.browse(sale_id)
        self.assertTrue(is_string(sale_mod.views_by_module))

    def test_field_text_write(self):
        # TODO
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
