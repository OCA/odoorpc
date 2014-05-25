# -*- coding: UTF-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2011-2013 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""This module provides the BrowseRecord class."""
from oerplib import error


class BrowseRecord(object):
    """Base class that all browsable records inherit from.
    No attributes should be defined in this class (except ``_id``/``id``,
    ``__oerp__``, ``__osv__``, ``__data__`` and Python magic methods) in order
    to not be conflicted with the fields defined in the model class on
    the server.

    A reference to the :class:`OERP <oerplib.OERP>` object used to instanciate
    a ``browse_record`` is available through the ``__oerp__`` attribute::

        >>> oerp = oerplib.OERP('localhost')
        >>> user = oerp.login('admin', 'admin', 'db_name')
        >>> user.__oerp__ == oerp
        True

    The ``__data__`` attribute is used to store some data related to the
    record (it is not recommended to edit them)::

        >>> user.__data__
        {'updated_values': {},
         'raw_data': {'action_id': False,
                      'active': True,
                      'company_id': [1, 'Your Company'],
                      ...},
         'values': {'action_id': False,
                    'active': True,
                    'company_id': [1, 'Your Company'],
                    ...}}

    In the same way, information about the model class and its columns may be
    obtained via the ``__osv__`` attribute::

        >>> user.__osv__
        {'columns': {'action_id': <oerplib.service.osv.fields.Many2OneField object at 0xb75786ec>,
                     'active': <oerplib.service.osv.fields.ValueField object at 0xb7598b6c>,
                     'company_id': <oerplib.service.osv.fields.Many2OneField object at 0xb757868c>,
                     ...},
         'name': 'res.users'}

    """
    __oerp__ = None
    __osv__ = None

    def __init__(self, o_id):
        self._id = o_id
        self.__data__ = {'values': {}, 'raw_data': {}, 'updated_values': {}}

    @property
    def id(self):
        """ID of the record."""
        return self._id

    def __repr__(self):
        return "browse_record(%r, %r)" % (self.__osv__['name'], self._id)

    def __getitem__(self, key):
        return getattr(self, key)

    def __int__(self):
        return self._id

    def __eq__(self, other):
        """Compare two browse records. Return ``True`` if their ID and model
        name are equals.

        NOTE: the comparison is made this way because their model classes can be
        differents objects.

        """
        return isinstance(other, BrowseRecord) and \
            self.id == other.id and \
            self.__osv__['name'] == other.__osv__['name']

    def __ne__(self, other):
        if not isinstance(other, BrowseRecord):
            return True
        return isinstance(other, BrowseRecord)\
            and (self.__osv__['name'], self.id) !=\
                (other.__osv__['name'], other.id)


class BrowseRecordIterator(object):
    """Iterator of browsable records.
    In fact, it is a generator to return records one by one, and able to
    increment/decrement records by overriding '+=' and '-=' operators.
    """
    def __init__(self, model, ids, context=None,
                 parent=None, parent_field=None):
        self.model = model
        self.ids = ids
        self.context = context
        self.index = None
        if self.ids:
            self.index = 0
        self.parent = parent
        self.parent_field = parent_field

    def __iter__(self):
        return self

    def next(self):
        if self.index is None or self.index >= len(self.ids):
            raise StopIteration
        else:
            id_ = self.ids[self.index]
            self.index += 1
            return self.model.browse(id_, context=self.context)

    def __iadd__(self, records):
        if not self.parent or not self.parent_field:
            raise error.InternalError("No parent record to update")
        try:
            list(records)
        except TypeError:
            records = [records]
        updated_values = self.parent.__data__['updated_values']
        res = []
        if updated_values.get(self.parent_field.name):
            res = updated_values[self.parent_field.name][:]  # Copy
        from oerplib.service.osv import fields
        for id_ in fields.records2ids(records):
            if (3, id_) in res:
                res.remove((3, id_))
            if (4, id_) not in res:
                res.append((4, id_))
        return res

    def __isub__(self, records):
        if not self.parent or not self.parent_field:
            raise error.InternalError("No parent record to update")
        try:
            list(records)
        except TypeError:
            records = [records]
        updated_values = self.parent.__data__['updated_values']
        res = []
        if updated_values.get(self.parent_field.name):
            res = updated_values[self.parent_field.name][:]  # Copy
        from oerplib.service.osv import fields
        for id_ in fields.records2ids(records):
            if (4, id_) in res:
                res.remove((4, id_))
            if (3, id_) not in res:
                res.append((3, id_))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
