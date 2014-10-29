# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model


class TestFieldOne2many(LoginTestCase):

    def setUp(self):
        LoginTestCase.setUp(self)
        self.partner_obj = self.odoo.env['res.partner']
        self.p0_id = self.partner_obj.create({'name': "Parent"})
        self.p1_id = self.partner_obj.create({'name': "Child 1"})
        self.p2_id = self.partner_obj.create({'name': "Child 2"})

    def test_field_one2many_read(self):
        # Test if empty field returns an empty recordset, and not False
        self.assertIsInstance(self.user.child_ids, Model)
        self.assertEqual(self.user.child_ids.ids, [])

    def test_field_one2many_write_set_false(self):
        partner = self.partner_obj.browse(self.p0_id)
        # = False
        partner.child_ids = False
        data = partner.read(['child_ids'])[0]
        self.assertEqual(data['child_ids'], [])
        self.assertEqual(list(partner.child_ids), [])

    def test_field_one2many_write_set_empty_list(self):
        partner = self.partner_obj.browse(self.p0_id)
        # = []
        partner.child_ids = []
        data = partner.read(['child_ids'])[0]
        self.assertEqual(data['child_ids'], [])
        self.assertEqual(list(partner.child_ids), [])

    def test_field_one2many_write_set_magic_tuples(self):
        partner = self.partner_obj.browse(self.p0_id)
        # = [(6, 0, IDS)]
        data = partner.read(['child_ids'])[0]
        self.assertEqual(data['child_ids'], [])
        partner.child_ids = [(6, 0, [self.p1_id])]
        data = partner.read(['child_ids'])[0]
        self.assertEqual(data['child_ids'], [self.p1_id])
        partner_ids = [acc.id for acc in partner.child_ids]
        self.assertEqual(partner_ids, [self.p1_id])

    def test_field_one2many_write_iadd_id(self):
        partner = self.partner_obj.browse(self.p0_id)
        # += ID
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner.child_ids += self.p1_id
        partner.child_ids += self.p2_id
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        self.assertIn(self.p1_id, [pt.id for pt in partner.child_ids])
        self.assertIn(self.p2_id, [pt.id for pt in partner.child_ids])
        self.assertEqual(len(partner.child_ids), 2)

    def test_field_one2many_write_iadd_record(self):
        partner = self.partner_obj.browse(self.p0_id)
        # += Record
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner.child_ids += self.partner_obj.browse(self.p2_id)
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertIn(self.p2_id, partner_ids)
        self.assertEqual(len(partner.child_ids), 1)

    def test_field_one2many_write_iadd_recordset(self):
        partner = self.partner_obj.browse(self.p0_id)
        # += Recordset
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner.child_ids += self.partner_obj.browse([self.p1_id, self.p2_id])
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertIn(self.p1_id, partner_ids)
        self.assertIn(self.p2_id, partner_ids)
        self.assertEqual(len(partner.child_ids), 2)

    def test_field_one2many_write_iadd_list_ids(self):
        partner = self.partner_obj.browse(self.p0_id)
        # += List of IDs
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner.child_ids += [self.p1_id, self.p2_id]
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertIn(self.p1_id, partner_ids)
        self.assertIn(self.p2_id, partner_ids)
        self.assertEqual(len(partner.child_ids), 2)

    def test_field_one2many_write_iadd_list_records(self):
        partner = self.partner_obj.browse(self.p0_id)
        # += List of records
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner.child_ids += [self.partner_obj.browse(self.p1_id),
                              self.partner_obj.browse(self.p2_id)]
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertIn(self.p1_id, partner_ids)
        self.assertIn(self.p2_id, partner_ids)
        self.assertEqual(len(partner.child_ids), 2)

    def test_field_one2many_write_iadd_id_and_list_ids(self):
        partner = self.partner_obj.browse(self.p0_id)
        # += ID and += [ID]
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner.child_ids += self.p1_id
        partner.child_ids += [self.p2_id]
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertIn(self.p1_id, partner_ids)
        self.assertIn(self.p2_id, partner_ids)
        self.assertEqual(len(partner.child_ids), 2)

    def test_field_one2many_write_isub_id(self):
        partner = self.partner_obj.browse(self.p0_id)
        partner.child_ids = [self.p1_id, self.p2_id]
        # -= ID
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner.child_ids -= self.p1_id
        partner.child_ids -= self.p2_id
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertNotIn(self.p2_id, partner_ids)

    def test_field_one2many_write_isub_record(self):
        partner = self.partner_obj.browse(self.p0_id)
        partner.child_ids = [self.p1_id, self.p2_id]
        # -= Record
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner.child_ids -= self.partner_obj.browse(self.p1_id)
        partner.child_ids -= self.partner_obj.browse(self.p2_id)
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertNotIn(self.p2_id, partner_ids)

    def test_field_one2many_write_isub_recordset(self):
        partner = self.partner_obj.browse(self.p0_id)
        partner.child_ids = [self.p1_id, self.p2_id]
        # -= Recordset
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner.child_ids -= self.partner_obj.browse([self.p1_id, self.p2_id])
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertNotIn(self.p2_id, partner_ids)

    def test_field_one2many_write_isub_list_ids(self):
        partner = self.partner_obj.browse(self.p0_id)
        partner.child_ids = [self.p1_id, self.p2_id]
        childs = self.partner_obj.browse([self.p1_id, self.p2_id])
        # -= List of IDs
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner.child_ids -= childs.ids
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertNotIn(self.p2_id, partner_ids)

    def test_field_one2many_write_isub_list_records(self):
        partner = self.partner_obj.browse(self.p0_id)
        partner.child_ids = [self.p1_id, self.p2_id]
        childs = [self.partner_obj.browse(self.p1_id),
                  self.partner_obj.browse(self.p2_id)]
        # -= List of records
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner.child_ids -= childs
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertNotIn(self.p2_id, partner_ids)

    def test_field_one2many_write_isub_id_and_list_ids(self):
        partner = self.partner_obj.browse(self.p0_id)
        partner.child_ids = [self.p1_id, self.p2_id]
        # -= ID and -= [ID]
        data = partner.read(['child_ids'])[0]
        self.assertIn(self.p1_id, data['child_ids'])
        self.assertIn(self.p2_id, data['child_ids'])
        partner.child_ids -= self.p1_id
        partner.child_ids -= [self.p2_id]
        data = partner.read(['child_ids'])[0]
        self.assertNotIn(self.p1_id, data['child_ids'])
        self.assertNotIn(self.p2_id, data['child_ids'])
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(self.p1_id, partner_ids)
        self.assertNotIn(self.p2_id, partner_ids)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
