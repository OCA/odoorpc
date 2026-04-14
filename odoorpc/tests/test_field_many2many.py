# -*- coding: utf-8 -*-

import time

from odoorpc.models import Model
from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestFieldMany2many(LoginTestCase):
    def setUp(self):
        LoginTestCase.setUp(self)
        self.group_obj = self.odoo.env["res.groups"]
        self.u0_id = self._create(
            "res.users",
            {
                "name": "TestMany2many User 1",
                "login": "test_m2m_u1_%s" % time.time(),
            },
        )
        self.g1_id = self._create("res.groups", {"name": "Group 1"})
        self.g2_id = self._create("res.groups", {"name": "Group 2"})
        if v(self.odoo.version)[0] >= 19:
            self.groups_field = "group_ids"
        else:
            self.groups_field = "groups_id"
        self.u1_id = self._create(
            "res.users",
            {
                "name": "TestMany2many User 2",
                "login": "test_m2m_u2_%s" % time.time(),
                self.groups_field: [(4, self.g1_id), (4, self.g2_id)],
            },
        )

    def _get_user_groups(self, user):
        """Helper method getting groups field from `user` record."""
        return getattr(user, self.groups_field)

    def _set_user_groups(self, user, groups):
        """Helper method setting `groups` on `user` record."""
        setattr(user, self.groups_field, groups)

    def _iadd_user_groups(self, user, groups):
        """Helper method adding groups field on `user` record with += operator."""
        if v(self.odoo.version)[0] < 19:
            user.groups_id += groups
        else:
            user.group_ids += groups

    def _isub_user_groups(self, user, groups):
        """Helper method subtracting groups field from `user` record with -= operator."""
        if v(self.odoo.version)[0] < 19:
            user.groups_id -= groups
        else:
            user.group_ids -= groups

    def _read_user_groups(self, user):
        """Helper method reading groups from `user` with `read` method."""
        data = self._read(user._name, user.ids, [self.groups_field])[0]
        return data[self.groups_field]

    def test_field_many2many_read(self):
        self.assertIsInstance(self.user.company_ids, Model)
        self.assertEqual(self.user.company_ids._name, "res.company")
        # Test if empty field returns an empty recordset, and not False
        self.assertIsInstance(self.user.message_follower_ids, Model)
        self.assertEqual(self.user.message_follower_ids.ids, [])
        self.assertFalse(bool(self.user.message_follower_ids))

    def test_field_many2many_write_set_false(self):
        user = self.user_obj.browse(self.u0_id)
        # False
        self._set_user_groups(user, False)
        groups = self._read_user_groups(user)
        self.assertEqual(groups, [])
        self.assertEqual(list(self._get_user_groups(user)), [])

    def test_field_many2many_write_set_empty_list(self):
        user = self.user_obj.browse(self.u0_id)
        # = []
        self._set_user_groups(user, [])
        groups = self._read_user_groups(user)
        self.assertEqual(groups, [])
        self.assertEqual(list(self._get_user_groups(user)), [])

    def test_field_many2many_write_set_magic_tuples(self):
        user = self.user_obj.browse(self.u0_id)
        # [(6, 0, IDS)]
        self._set_user_groups(user, [(6, 0, [self.g1_id, self.g2_id])])
        groups = self._read_user_groups(user)
        self.assertIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        self.assertEqual(len(groups), 2)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)
        self.assertEqual(len(group_ids), 2)

    def test_field_many2many_write_iadd_id(self):
        user = self.user_obj.browse(self.u0_id)
        # += ID
        self._iadd_user_groups(user, self.g1_id)
        self._iadd_user_groups(user, self.g2_id)
        groups = self._read_user_groups(user)
        self.assertIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_record(self):
        user = self.user_obj.browse(self.u0_id)
        # += Record
        self._iadd_user_groups(user, self.group_obj.browse(self.g2_id))
        groups = self._read_user_groups(user)
        self.assertNotIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertNotIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_recordset(self):
        user = self.user_obj.browse(self.u0_id)
        # += Recordset
        self._iadd_user_groups(user, self.group_obj.browse([self.g1_id, self.g2_id]))
        groups = self._read_user_groups(user)
        self.assertIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_list_ids(self):
        user = self.user_obj.browse(self.u0_id)
        # += List of IDs
        self._iadd_user_groups(user, [self.g1_id, self.g2_id])
        groups = self._read_user_groups(user)
        self.assertIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_list_records(self):
        user = self.user_obj.browse(self.u0_id)
        # += List of records
        self._iadd_user_groups(
            user,
            [
                self.group_obj.browse(self.g1_id),
                self.group_obj.browse(self.g2_id),
            ],
        )
        groups = self._read_user_groups(user)
        self.assertIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_iadd_id_and_list_ids(self):
        user = self.user_obj.browse(self.u0_id)
        # += ID and += [ID]
        self._iadd_user_groups(user, self.g1_id)
        self._iadd_user_groups(user, [self.g2_id])
        groups = self._read_user_groups(user)
        self.assertIn(self.g1_id, groups)
        self.assertIn(self.g2_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertIn(self.g1_id, group_ids)
        self.assertIn(self.g2_id, group_ids)

    def test_field_many2many_write_isub_id(self):
        user = self.user_obj.browse(self.u1_id)
        self.assertIn(self.g1_id, self._get_user_groups(user).ids)
        # -= ID
        self._isub_user_groups(user, self.g1_id)
        groups = self._read_user_groups(user)
        self.assertNotIn(self.g1_id, groups)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertNotIn(self.g1_id, group_ids)

    def test_field_many2many_write_isub_record(self):
        user = self.user_obj.browse(self.u1_id)
        self.assertIn(self.g1_id, self._get_user_groups(user).ids)
        # -= Record
        group = self.group_obj.browse(self.g1_id)
        self._isub_user_groups(user, group)
        groups = self._read_user_groups(user)
        self.assertNotIn(group.id, groups)
        self.assertNotIn(group.id, self._get_user_groups(user).ids)

    def test_field_many2many_write_isub_recordset(self):
        user = self.user_obj.browse(self.u1_id)
        groups = self.group_obj.browse([self.g1_id, self.g2_id])
        # -= Recordset
        groups_ = self._read_user_groups(user)
        self.assertIn(groups.ids[0], groups_)
        self.assertIn(groups.ids[1], groups_)
        self._isub_user_groups(user, groups)
        groups_ = self._read_user_groups(user)
        self.assertNotIn(groups.ids[0], groups_)
        self.assertNotIn(groups.ids[1], groups_)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

    def test_field_many2many_write_isub_list_ids(self):
        user = self.user_obj.browse(self.u1_id)
        groups = self.group_obj.browse([self.g1_id, self.g2_id])
        # -= List of IDs
        groups_ = self._read_user_groups(user)
        self.assertIn(groups.ids[0], groups_)
        self.assertIn(groups.ids[1], groups_)
        self._isub_user_groups(user, groups.ids)
        groups_ = self._read_user_groups(user)
        self.assertNotIn(groups.ids[0], groups_)
        self.assertNotIn(groups.ids[1], groups_)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

    def test_field_many2many_write_isub_list_records(self):
        user = self.user_obj.browse(self.u1_id)
        groups = self.group_obj.browse([self.g1_id, self.g2_id])
        # -= List of records
        groups_ = self._read_user_groups(user)
        self.assertIn(groups.ids[0], groups_)
        self.assertIn(groups.ids[1], groups_)
        self._isub_user_groups(user, [grp for grp in groups])
        groups_ = self._read_user_groups(user)
        self.assertNotIn(groups.ids[0], groups_)
        self.assertNotIn(groups.ids[1], groups_)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)

    def test_field_many2many_write_isub_id_and_list_ids(self):
        user = self.user_obj.browse(self.u1_id)
        groups = self.group_obj.browse([self.g1_id, self.g2_id])
        # -= ID and -= [ID]
        groups_ = self._read_user_groups(user)
        self.assertIn(groups.ids[0], groups_)
        self.assertIn(groups.ids[1], groups_)
        self._isub_user_groups(user, groups.ids[0])
        self._isub_user_groups(user, [groups.ids[1]])
        groups_ = self._read_user_groups(user)
        self.assertNotIn(groups.ids[0], groups_)
        self.assertNotIn(groups.ids[1], groups_)
        group_ids = [grp.id for grp in self._get_user_groups(user)]
        self.assertNotIn(groups.ids[0], group_ids)
        self.assertNotIn(groups.ids[1], group_ids)
