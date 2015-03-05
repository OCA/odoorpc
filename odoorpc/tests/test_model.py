# -*- coding: UTF-8 -*-

import time

from odoorpc.tests import LoginTestCase
from odoorpc import error
from odoorpc.models import Model
from odoorpc.env import Environment


class TestModel(LoginTestCase):

    def setUp(self):
        LoginTestCase.setUp(self)
        self.partner_obj = self.odoo.env['res.partner']
        self.p0_id = self.partner_obj.create({'name': "Parent"})
        self.p1_id = self.partner_obj.create({'name': "Child 1"})
        self.p2_id = self.partner_obj.create({'name': "Child 2"})
        self.group_obj = self.odoo.env['res.groups']
        self.u0_id = self.user_obj.create(
            {'name': "TestOdooRPC", 'login': 'test_%s' % time.time()})
        self.g1_id = self.group_obj.create({'name': "Group 1"})
        self.g2_id = self.group_obj.create({'name': "Group 2"})

    def test_create_model_class(self):
        partner_obj = self.odoo.env['res.partner']
        self.assertEqual(partner_obj._name, 'res.partner')
        self.assertIn('name', partner_obj._columns)
        self.assertIsInstance(partner_obj.env, Environment)

    def test_model_browse(self):
        partner = self.partner_obj.browse(1)
        self.assertIsInstance(partner, Model)
        self.assertEqual(partner.id, 1)
        self.assertEqual(partner.ids, [1])
        self.assertEqual(partner.env, self.partner_obj.env)
        partners = self.partner_obj.browse([1])
        self.assertIsInstance(partners, Model)
        self.assertEqual(partners.id, 1)
        self.assertEqual(partners.ids, [1])
        self.assertEqual(partners.env, self.partner_obj.env)
        self.assertEqual(partners.ids, partner.ids)

    def test_model_browse_false(self):
        partner = self.partner_obj.browse(False)
        self.assertEqual(len(partner), 0)

    def test_model_browse_wrong_id(self):
        self.assertRaises(
            ValueError,
            self.partner_obj.browse,
            9999999)    # Wrong ID
        self.assertRaises(
            error.RPCError,
            self.partner_obj.browse,
            "1")  # Wrong ID type

    def test_model_browse_without_arg(self):
        self.assertRaises(TypeError, self.partner_obj.browse)

    def test_model_rpc_method(self):
        user_obj = self.odoo.env['res.users']
        user_obj.name_get(self.odoo.env.uid)
        self.odoo.env['ir.sequence'].get('fake.code')  # Return False

    def test_model_rpc_method_error_no_arg(self):
        # Handle exception (execute a 'name_get' with without args)
        user_obj = self.odoo.env['res.users']
        self.assertRaises(
            error.RPCError,
            user_obj.name_get)  # No arg

    def test_model_rpc_method_error_wrong_args(self):
        # Handle exception (execute a 'search' with wrong args)
        user_obj = self.odoo.env['res.users']
        self.assertRaises(
            error.RPCError,
            user_obj.search,
            False)  # Wrong arg

    def test_record_getitem_field(self):
        partner = self.partner_obj.browse(1)
        self.assertEqual(partner['id'], 1)
        self.assertEqual(partner['name'], partner.name)

    def test_record_getitem_integer(self):
        partner = self.partner_obj.browse(1)
        self.assertEqual(partner[0], partner)

    def test_record_getitem_slice(self):
        partner = self.partner_obj.browse(1)
        self.assertEqual([record.id for record in partner[:]], [1])

    def test_record_iter(self):
        ids = self.partner_obj.search([])[:5]
        partners = self.partner_obj.browse(ids)
        self.assertEqual(set([partner.id for partner in partners]), set(ids))
        partner = partners[0]
        self.assertIn(partner.id, partners.ids)
        self.assertEqual(id(partner._values), id(partners._values))

    def test_record_with_context(self):
        user = self.odoo.env.user
        self.assertEqual(user.env.lang, 'en_US')
        user_fr = user.with_context(lang='fr_FR')
        self.assertEqual(user_fr.env.lang, 'fr_FR')
        # Install 'fr_FR' and test the use of context with it
        Wizard = self.odoo.env['base.language.install']
        wiz_id = Wizard.create({'lang': 'fr_FR'})
        Wizard.lang_install([wiz_id])
        # Read data with two languages
        Country = self.odoo.env['res.country']
        de_id = Country.search([('code', '=', 'DE')])[0]
        de = Country.browse(de_id)
        self.assertEqual(de.name, 'Germany')
        self.assertEqual(de.with_context(lang='fr_FR').name, 'Allemagne')
        # Write data with two languages
        Product = self.odoo.env['product.product']
        self.assertEqual(Product.env.lang, 'en_US')
        name_en = "Product en_US"
        product_id = Product.create({'name': name_en})
        product_en = Product.browse(product_id)
        self.assertEqual(product_en.name, name_en)
        product_fr = product_en.with_context(lang='fr_FR')
        self.assertEqual(product_fr.env.lang, 'fr_FR')
        name_fr = "Produit fr_FR"
        product_fr.write({'name': name_fr})
        product_fr = product_fr.with_context()  # Refresh the recordset
        self.assertEqual(product_fr.name, name_fr)
        self.assertEqual(Product.env.lang, 'en_US')
        product_en = Product.browse(product_id)
        self.assertEqual(product_en.name, name_en)
        new_name_fr = "%s (nouveau)" % name_fr
        product_fr.name = new_name_fr
        product_fr = product_fr.with_context()  # Refresh the recordset
        self.assertEqual(product_fr.name, new_name_fr)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
