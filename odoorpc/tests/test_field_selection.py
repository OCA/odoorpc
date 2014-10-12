# -*- coding: UTF-8 -*-

from odoorpc.tests import LoginTestCase


class TestFieldSelection(LoginTestCase):

    def test_field_selection_read(self):
        self.assertEqual(self.user.state, 'active')

    def test_field_selection_write(self):
        # TODO: split in several unit tests
        #record = self.user
        #data = record.__class__.fields_get()
        #for f in data:
        #    if data[f]['type'] == 'selection':
        #        print("%s" % (f))
        #        #print("%s - %s" % (f, self.user[f]))
        backup = self.user.tz
        # False
        self.user.tz = False
        data = self.user.read(['tz'])[0]
        self.assertEqual(data['tz'], False)
        self.assertEqual(self.user.tz, False)
        # None
        self.user.tz = None
        data = self.user.read(['tz'])[0]
        self.assertEqual(data['tz'], False)
        self.assertEqual(self.user.tz, False)
        # Europe/Paris
        self.user.tz = 'Europe/Paris'
        data = self.user.read(['tz'])[0]
        self.assertEqual(data['tz'], 'Europe/Paris')
        self.assertEqual(self.user.tz, 'Europe/Paris')
        # Restore original value
        self.user.tz = backup
        data = self.user.read(['tz'])[0]
        self.assertEqual(data['tz'], backup)
        self.assertEqual(self.user.tz, backup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
