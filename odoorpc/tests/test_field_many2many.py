# -*- coding: UTF-8 -*-

import time

from odoorpc.tests import LoginTestCase
from odoorpc.models import Model


class TestFieldMany2many(LoginTestCase):

    def setUp(self):
        LoginTestCase.setUp(self)
        self.group_obj = self.odoo.env['res.groups']
        self.u0_id = self.user_obj.create(
            {'name': "TestMany2many", 'login': 'test_m2m_%s' % time.time()})
        self.g1_id = self.group_obj.create({'name': "Group 1"})
        self.g2_id = self.group_obj.create({'name': "Group 2"})

    def test_field_many2many_read(self):
        self.assertIsInstance(self.user.company_ids, Model)
        self.assertEqual(self.user.company_ids._name, 'res.company')
        # Test if empty field returns an empty recordset, and not False
        self.assertIsInstance(self.user.message_follower_ids, Model)
        self.assertEqual(self.user.message_follower_ids.ids, [])
        self.assertFalse(bool(self.user.message_follower_ids))

    def test_field_many2many_write_set_false(self):
        user = self.user_obj.browse(self.u0_id)
        # False
        user.groups_id = False
        data = user.read(['groups_id'])[0]
        self.assertEqual(data['groups_id'], [])
        self.assertEqual(list(user.groups_id), [])

    def test_field_many2many_write_set_empty_list(self):
        user = self.user_obj.browse(self.u0_id)
        # = []
        user.groups_id = []
        data = user.read(['groups_id'])[0]
        self.assertEqual(data['groups_id'], [])
        self.assertEqual(list(user.groups_id), [])

    def test_field_many2many_write_set_magic_tuples(self):
        user = self.user_obj.browse(self.u0_id)
        # [(6, 0, IDS)]
        user.groups_id = [(6, 0, [self.g1_id, self.g2_id])]
        data = user.read(['groups_id'])[0]
        self.assertIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        self.assertEqual(len(data['groups_id']), 2)
        group_ids = [grp.id for grp in user.groups_id]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)
        self.assertEqual(len(group_ids), 2)

    def test_field_many2many_write_iadd_id(self):
        user = self.user_obj.browse(self.u0_id)
        # += ID
        user.groups_id += self.g1_id
        user.groups_id += self.g2_id
        data = user.read(['groups_id'])[0]
        self.assertIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_record(self):
        user = self.user_obj.browse(self.u0_id)
        # += Record
        user.groups_id += self.group_obj.browse(self.g2_id)
        data = user.read(['groups_id'])[0]
        self.assertNotIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_recordset(self):
        user = self.user_obj.browse(self.u0_id)
        # += Recordset
        user.groups_id += self.group_obj.browse([self.g1_id, self.g2_id])
        data = user.read(['groups_id'])[0]
        self.assertIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_list_ids(self):
        user = self.user_obj.browse(self.u0_id)
        # += List of IDs
        user.groups_id += [self.g1_id, self.g2_id]
        data = user.read(['groups_id'])[0]
        self.assertIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_list_records(self):
        user = self.user_obj.browse(self.u0_id)
        # += List of records
        user.groups_id += [self.group_obj.browse(self.g1_id),
                           self.group_obj.browse(self.g2_id)]
        data = user.read(['groups_id'])[0]
        self.assertIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_id_and_list_ids(self):
        user = self.user_obj.browse(self.u0_id)
        # += ID and += [ID]
        user.groups_id += self.g1_id
        user.groups_id += [self.g2_id]
        data = user.read(['groups_id'])[0]
        self.assertIn(self.g1_id, data['groups_id'])
        self.assertIn(self.g2_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_isub_id(self):
        user = self.user_obj.browse(self.u0_id)
        group_id = user.read(['groups_id'])[0]['groups_id'][0]
        # -= ID
        user.groups_id -= group_id
        data = user.read(['groups_id'])[0]
        self.assertNotIn(group_id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(group_id, group_ids)

    def test_field_many2many_write_isub_record(self):
        user = self.user_obj.browse(self.u0_id)
        group = user.groups_id[0]
        # -= Record
        data = user.read(['groups_id'])[0]
        self.assertIn(group.id, data['groups_id'])
        user.groups_id -= group
        data = user.read(['groups_id'])[0]
        self.assertNotIn(group.id, data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(group.id, group_ids)

    def test_field_many2many_write_isub_recordset(self):
        user = self.user_obj.browse(self.u0_id)
        groups = user.groups_id
        # -= Recordset
        data = user.read(['groups_id'])[0]
        self.assertIn(groups.ids[0], data['groups_id'])
        self.assertIn(groups.ids[1], data['groups_id'])
        user.groups_id -= groups
        data = user.read(['groups_id'])[0]
        self.assertNotIn(groups.ids[0], data['groups_id'])
        self.assertNotIn(groups.ids[1], data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

    def test_field_many2many_write_isub_list_ids(self):
        user = self.user_obj.browse(self.u0_id)
        groups = user.groups_id
        # -= List of IDs
        data = user.read(['groups_id'])[0]
        self.assertIn(groups.ids[0], data['groups_id'])
        self.assertIn(groups.ids[1], data['groups_id'])
        user.groups_id -= groups.ids
        data = user.read(['groups_id'])[0]
        self.assertNotIn(groups.ids[0], data['groups_id'])
        self.assertNotIn(groups.ids[1], data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

    def test_field_many2many_write_isub_list_records(self):
        user = self.user_obj.browse(self.u0_id)
        groups = user.groups_id
        # -= List of records
        data = user.read(['groups_id'])[0]
        self.assertIn(groups.ids[0], data['groups_id'])
        self.assertIn(groups.ids[1], data['groups_id'])
        user.groups_id -= [grp for grp in groups]
        data = user.read(['groups_id'])[0]
        self.assertNotIn(groups.ids[0], data['groups_id'])
        self.assertNotIn(groups.ids[1], data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

    def test_field_many2many_write_isub_id_and_list_ids(self):
        user = self.user_obj.browse(self.u0_id)
        groups = user.groups_id
        # -= ID and -= [ID]
        data = user.read(['groups_id'])[0]
        self.assertIn(groups.ids[0], data['groups_id'])
        self.assertIn(groups.ids[1], data['groups_id'])
        user.groups_id -= groups.ids[0]
        user.groups_id -= [groups.ids[1]]
        data = user.read(['groups_id'])[0]
        self.assertNotIn(groups.ids[0], data['groups_id'])
        self.assertNotIn(groups.ids[1], data['groups_id'])
        group_ids = [grp.id for grp in user.groups_id]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
