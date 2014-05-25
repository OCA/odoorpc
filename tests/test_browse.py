# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import datetime

from args import ARGS

import oerplib
from oerplib.tools import v


class TestBrowse(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_browse_with_one_id(self):
        # Check the result returned
        result = self.oerp.browse('res.users', self.user.id)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(self.user, result)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        result = self.oerp.browse('res.users', self.user.id, context)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(self.user, result)

    def test_browse_with_ids(self):
        # Iteration
        for result in self.oerp.browse('res.users', [self.user.id]):
            self.assertEqual(self.user, result)
        user_ids = self.oerp.search('res.users', [])
        for result in self.oerp.browse('res.users', user_ids):
            self.assertIsInstance(
                result, oerplib.service.osv.browse.BrowseRecord)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        for result in self.oerp.browse('res.users', user_ids, context):
            self.assertIsInstance(
                result, oerplib.service.osv.browse.BrowseRecord)

    def test_browse_with_id_false(self):
        # Check the result returned
        result = self.oerp.browse('res.users', False)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(False, result.id)
        # With context
        context = self.oerp.execute('res.users', 'context_get')
        result = self.oerp.browse('res.users', False, context)
        self.assertIsInstance(result, oerplib.service.osv.browse.BrowseRecord)
        self.assertEqual(False, result.id)

    def test_browse_with_wrong_id(self):
        # Handle exception (execute a 'browse' with wrong ID)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.browse,
            'res.users',
            999999999)

    def test_browse_without_args(self):
        # Handle exception (execute a 'browse' without args)
        self.assertRaises(
            TypeError,
            self.oerp.browse,
            'res.users')

    def test_browse_with_wrong_args(self):
        # Handle exception (execute a 'browse' with wrong args)
        self.assertRaises(
            oerplib.error.RPCError,
            self.oerp.browse,
            'res.users',
            "wrong_arg")  # Wrong arg

    def test_reset(self):
        # Check the result returned
        self.user.name = "Charly"
        self.oerp.reset(self.user)
        self.assertEqual(self.user.name, "Administrator")

    def test_refresh(self):
        # Check the result returned
        self.user.name = "Charly"
        self.oerp.refresh(self.user)
        self.assertEqual(self.user.name, "Administrator")

    def test_write_record_char(self):
        backup_name = self.user.name
        self.user.name = "Charly"
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.name, "Charly")
        self.user.name = backup_name
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.name, backup_name)

    def test_write_record_boolean(self):
        self.user.active = False
        self.user.active = True
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.active, True)

    def test_write_record_float(self):
        partner = self.user.company_id.partner_id
        partner.credit_limit = False
        self.oerp.write_record(partner)
        self.assertEqual(partner.credit_limit, 0.0)
        partner.credit_limit = 0.0
        self.oerp.write_record(partner)
        self.assertEqual(partner.credit_limit, 0.0)

    def test_write_record_integer(self):
        cur = self.oerp.browse('res.currency', 1)
        backup_accuracy = cur.accuracy
        cur.accuracy = False
        self.oerp.write_record(cur)
        self.assertEqual(cur.accuracy, 0)
        cur.accuracy = backup_accuracy
        self.oerp.write_record(cur)
        self.assertEqual(cur.accuracy, backup_accuracy)

    def test_write_record_selection(self):
        self.user.context_tz = False
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.context_tz, False)
        self.user.context_tz = 'Europe/Paris'
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.context_tz, 'Europe/Paris')

    def test_write_record_date(self):
        partner = self.user.company_id.partner_id
        partner.date = False
        self.oerp.write_record(partner)
        self.assertEqual(partner.date, False)
        partner.date = '2012-01-01'
        self.oerp.write_record(partner)
        self.assertEqual(partner.date, datetime.date(2012, 1, 1))
        partner.date = datetime.date(2012, 1, 1)
        self.oerp.write_record(partner)
        self.assertEqual(partner.date, datetime.date(2012, 1, 1))

    #def test_write_record_datetime(self):
    #    # No common model found in every versions of OpenERP with a
    #    # fields.datetime writable
    #    pass

    def test_write_record_many2many(self):
        backup_groups = list(self.user.groups_id)
        # False
        self.user.groups_id = False
        self.assertEqual(list(self.user.groups_id), [])
        self.oerp.reset(self.user)
        # []
        self.user.groups_id = []
        self.assertEqual(list(self.user.groups_id), [])
        self.oerp.reset(self.user)
        # [(6, 0, IDS)]
        self.user.groups_id = [(6, 0, [1, 2])]
        self.assertIn(1, [grp.id for grp in self.user.groups_id])
        self.assertIn(2, [grp.id for grp in self.user.groups_id])
        self.oerp.write_record(self.user)
        self.assertIn(1, [grp.id for grp in self.user.groups_id])
        self.assertIn(2, [grp.id for grp in self.user.groups_id])
        # Operator +=
        grp_obj = self.oerp.get('res.groups')
        self.user.groups_id += 4                        # ID
        self.assertIn(4, [grp.id for grp in self.user.groups_id])
        self.oerp.reset(self.user)
        self.user.groups_id += grp_obj.browse(4)        # Browse record
        self.assertIn(4, [grp.id for grp in self.user.groups_id])
        self.oerp.reset(self.user)
        self.user.groups_id += [4, 5]                   # List of IDs
        group_ids = [grp.id for grp in self.user.groups_id]
        self.assertIn(4, group_ids)
        self.assertIn(5, group_ids)
        self.oerp.reset(self.user)
        self.user.groups_id += list(grp_obj.browse([4, 5]))  # List of browse records
        group_ids = [grp.id for grp in self.user.groups_id]
        self.assertIn(4, group_ids)
        self.assertIn(5, group_ids)
        self.oerp.write_record(self.user)
        self.assertIn(4, group_ids)
        self.assertIn(5, group_ids)
        self.user.groups_id = False                     # Starting with no value
        self.user.groups_id += 4
        self.user.groups_id += [5]
        self.assertIn(4, [grp.id for grp in self.user.groups_id])
        self.assertIn(5, [grp.id for grp in self.user.groups_id])
        # Operator -=
        self.user.groups_id -= 1                        # ID
        self.assertNotIn(1, [grp.id for grp in self.user.groups_id])
        self.oerp.reset(self.user)
        self.user.groups_id -= grp_obj.browse(1)        # Browse record
        self.assertNotIn(1, [grp.id for grp in self.user.groups_id])
        self.oerp.reset(self.user)
        self.user.groups_id -= [1, 2]                   # List of IDs
        group_ids = [grp.id for grp in self.user.groups_id]
        self.assertNotIn(1, group_ids)
        self.assertNotIn(2, group_ids)
        self.oerp.reset(self.user)
        self.user.groups_id -= list(grp_obj.browse([1, 2]))  # List of browse records
        group_ids = [grp.id for grp in self.user.groups_id]
        self.assertNotIn(1, group_ids)
        self.assertNotIn(2, group_ids)
        self.oerp.write_record(self.user)
        self.assertNotIn(1, group_ids)
        self.assertNotIn(2, group_ids)
        self.user.groups_id = False                     # Starting with no value
        self.user.groups_id -= 1
        self.user.groups_id -= [5]
        self.assertEqual([], [grp.id for grp in self.user.groups_id])
        # Restore the original value
        self.user.groups_id = backup_groups
        self.assertEqual(list(self.user.groups_id), backup_groups)
        self.oerp.write_record(self.user)
        self.assertEqual(list(self.user.groups_id), backup_groups)

    def test_write_record_many2one(self):
        self.user.action_id = 1
        self.assertEqual(self.user.action_id.id, 1)
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.action_id.id, 1)
        action = self.oerp.get('ir.actions.actions').browse(1)
        self.user.action_id = action
        self.oerp.write_record(self.user)
        self.assertEqual(self.user.action_id.id, 1)
        # False
        self.user.action_id = False
        self.oerp.write_record(self.user)
        if v(self.oerp.version)[:2] == v('5.0'):
            self.assertEqual(self.user.action_id.id, 1)
        elif v(self.oerp.version)[:2] == v('6.0'):
            self.assertEqual(self.user.action_id, False)
        elif v(self.oerp.version)[:2] == v('6.1'):
            self.assertEqual(self.user.action_id, False)
        else:
            self.assertEqual(self.user.action_id, False)

    def test_write_record_one2many(self):
        partner_obj = self.oerp.get('res.partner')
        partner = partner_obj.browse(1)
        backup_childs = [acc for acc in partner.child_ids]
        p1_id = partner_obj.create({'name': "Test 1"})
        p2_id = partner_obj.create({'name': "Test 2"})
        # False
        partner.child_ids = False
        self.assertEqual(list(partner.child_ids), [])
        self.oerp.write_record(partner)
        self.assertEqual(list(partner.child_ids), [])
        # []
        partner.child_ids = []
        self.assertEqual(list(partner.child_ids), [])
        self.oerp.write_record(partner)
        self.assertEqual(list(partner.child_ids), [])
        # [(6, 0, IDS)]
        partner.child_ids = [(6, 0, [p1_id])]
        self.assertEqual([acc.id for acc in partner.child_ids], [p1_id])
        self.oerp.write_record(partner)
        self.assertEqual([acc.id for acc in partner.child_ids], [p1_id])
        # Operator +=
        partner.child_ids += p2_id                      # ID
        self.assertIn(p2_id, [pt.id for pt in partner.child_ids])
        self.oerp.reset(partner)
        partner.child_ids += partner_obj.browse(p2_id)  # Browse record
        self.assertIn(p2_id, [pt.id for pt in partner.child_ids])
        self.oerp.reset(partner)
        partner.child_ids += [p1_id, p2_id]             # List of IDs
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertIn(p1_id, partner_ids)
        self.assertIn(p2_id, partner_ids)
        self.oerp.reset(partner)
        partner.child_ids += list(partner_obj.browse([p1_id, p2_id]))   # List of browse records
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertIn(p1_id, partner_ids)
        self.assertIn(p2_id, partner_ids)
        self.oerp.write_record(partner)
        self.assertIn(p1_id, partner_ids)
        self.assertIn(p2_id, partner_ids)
        partner.child_ids = False                       # Starting with no value
        partner.child_ids += p1_id
        partner.child_ids += [p2_id]
        self.assertIn(p1_id, [pt.id for pt in partner.child_ids])
        self.assertIn(p2_id, [pt.id for pt in partner.child_ids])
        # Operator -=
        partner.child_ids -= p1_id                      # ID
        self.assertNotIn(p1_id, [pt.id for pt in partner.child_ids])
        self.oerp.reset(partner)
        partner.child_ids -= partner_obj.browse(p1_id)  # Browse record
        self.assertNotIn(p1_id, [pt.id for pt in partner.child_ids])
        self.oerp.reset(partner)
        partner.child_ids -= [p1_id, p2_id]             # List of IDs
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(p1_id, partner_ids)
        self.assertNotIn(p2_id, partner_ids)
        self.oerp.reset(partner)
        partner.child_ids -= list(partner_obj.browse([p1_id, p2_id]))   # List of browse records
        partner_ids = [pt.id for pt in partner.child_ids]
        self.assertNotIn(p1_id, partner_ids)
        self.assertNotIn(p2_id, partner_ids)
        self.oerp.write_record(partner)
        self.assertNotIn(p1_id, partner_ids)
        self.assertNotIn(p2_id, partner_ids)
        partner.child_ids = False                       # Starting with no value
        partner.child_ids -= p1_id
        partner.child_ids -= [p2_id]
        self.assertEqual([], [pt.id for pt in partner.child_ids])
        # Restore the original value
        partner.child_ids = backup_childs
        self.assertEqual(list(partner.child_ids), backup_childs)
        self.oerp.write_record(partner)
        self.assertEqual(list(partner.child_ids), backup_childs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
