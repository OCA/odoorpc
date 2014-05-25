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
"""This module contains classes representing the fields supported by OpenObject.
A field is a Python descriptor which defines getter/setter methods for
its related attribute.
"""
import datetime

from oerplib import error
from oerplib.service.osv import browse


def is_int(value):
    """Return `True` if ``value`` is an integer."""
    if isinstance(value, bool):
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False


def oerp_tuple_in(iterable):
    """Return `True` if `iterable` contains an expected tuple like
    ``(6, 0, IDS)`` (and so on).

        >>> oerp_tuple_in([0, 1, 2])        # Simple list
        False
        >>> oerp_tuple_in([(6, 0, [42])])   # List of tuples
        True
        >>> oerp_tuple_in([[1, 42]])        # List of lists
        True
    """
    if not iterable:
        return False
    def is_oerp_tuple(elt):
        try:
            return elt[:1][0] in [1, 2, 3, 4, 5] \
                    or elt[:2] in [(6, 0), [6, 0], (0, 0), [0, 0]]
        except:
            return False
    return any(is_oerp_tuple(elt) for elt in iterable)


def records2ids(iterable):
    """Replace `browse_records` contained in `iterable` by their
    corresponding IDs:

        >>> groups = list(oerp.user.groups_id)
        >>> records2ids(groups)
        [1, 2, 3, 14, 17, 18, 19, 7, 8, 9, 5, 20, 21, 22, 23]
    """
    def record2id(elt):
        if isinstance(elt, browse.BrowseRecord):
            return elt.id
        return elt
    return [record2id(elt) for elt in iterable]


class BaseField(object):
    """Field which all other fields inherit.
    Manage common metadata.
    """
    def __init__(self, osv, name, data):
        self.osv = osv
        self.name = name
        self.type = 'type' in data and data['type'] or False
        self.string = 'string' in data and data['string'] or False
        self.size = 'size' in data and data['size'] or False
        self.required = 'required' in data and data['required'] or False
        self.readonly = 'readonly' in data and data['readonly'] or False
        self.help = 'help' in data and data['help'] or False
        self.states = 'states' in data and data['states'] or False

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass

    def __str__(self):
        """Return a human readable string representation of the field."""
        attrs = ['string', 'relation', 'required', 'readonly', 'size', 'domain']
        attrs_rep = []
        for attr in attrs:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if value:
                    if isinstance(value, basestring):
                        attrs_rep.append("{0}='{1}'".format(attr, value))
                    else:
                        attrs_rep.append("{0}={1}".format(attr, value))
        attrs_rep = ", ".join(attrs_rep)
        return "{0}({1})".format(self.type, attrs_rep)

    def check_value(self, value):
        """Check the validity of a value for the field."""
        #if self.readonly:
        #    raise error.Error(
        #        "'{field_name}' field is readonly".format(
        #            field_name=self.name))
        if value and self.size:
            if not isinstance(value, basestring):
                raise ValueError("Value supplied has to be a string")
            if len(value) > self.size:
                raise ValueError(
                    "Lenght of the '{field_name}' is limited to {size}".format(
                        field_name=self.name,
                        size=self.size))
        if not value and self.required:
            raise ValueError(
                "'{field_name}' field is required".format(
                    field_name=self.name))
        return value


class SelectionField(BaseField):
    """Represent the OpenObject 'fields.selection'"""
    def __init__(self, osv, name, data):
        super(SelectionField, self).__init__(osv, name, data)
        self.selection = 'selection' in data and data['selection'] or False

    def __get__(self, instance, owner):
        if self.name in instance.__data__['updated_values']:
            return instance.__data__['updated_values'][self.name]
        return instance.__data__['values'][self.name]

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance.__data__['updated_values'][self.name] = value

    def check_value(self, value):
        super(SelectionField, self).check_value(value)
        selection = [val[0] for val in self.selection]
        if value and value not in selection:
            raise ValueError(
                "The value '{value}' supplied doesn't match with the possible "
                "values '{selection}' for the '{field_name}' field".format(
                    value=value,
                    selection=selection,
                    field_name=self.name,
                ))
        return value


class Many2ManyField(BaseField):
    """Represent the OpenObject 'fields.many2many'"""
    def __init__(self, osv, name, data):
        super(Many2ManyField, self).__init__(osv, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        """Return a generator to iterate on ``browse_record`` instances."""
        ids = None
        if instance.__data__['values'][self.name]:
            ids = instance.__data__['values'][self.name][:]
        # None value => get the value on the fly
        if ids is None:
            orig_ids = instance.__oerp__.read(
                instance.__osv__['name'],
                [instance.id], [self.name])[0][self.name]
            instance.__data__['values'][self.name] = orig_ids
            ids = orig_ids and orig_ids[:] or []
        # Take updated values into account
        if self.name in instance.__data__['updated_values']:
            ids = ids or []
            values = instance.__data__['updated_values'][self.name]
            # Handle OERP tuples to update 'ids'
            for value in values:
                if value[0] == 6 and value[2]:
                    ids = value[2]
                elif value[0] == 5:
                    ids = []
                elif value[0] == 4 and value[1] and value[1] not in ids:
                    ids.append(value[1])
                elif value[0] == 3 and value[1] and value[1] in ids:
                    ids.remove(value[1])
        context = instance.__data__['context'].copy()
        context.update(self.context)
        return browse.BrowseRecordIterator(
            model=instance.__oerp__.get(self.relation),
            ids=ids,
            context=context,
            parent=instance,
            parent_field=self)

    def __set__(self, instance, value):
        value = self.check_value(value)
        if value and not oerp_tuple_in(value):
            value = [(6, 0, records2ids(value))]
        elif not value:
            value = [(5, )]
        instance.__data__['updated_values'][self.name] = value

    def check_value(self, value):
        if value:
            if not isinstance(value, list):
                raise ValueError(
                    "The value supplied has to be a list or 'False'")
        return super(Many2ManyField, self).check_value(value)


class Many2OneField(BaseField):
    """Represent the OpenObject 'fields.many2one'"""
    def __init__(self, osv, name, data):
        super(Many2OneField, self).__init__(osv, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        id_ = instance.__data__['values'][self.name]
        if self.name in instance.__data__['updated_values']:
            id_ = instance.__data__['updated_values'][self.name]
            # FIXME if id_ is a browse_record
        # None value => get the value on the fly
        if id_ is None:
            id_ = instance.__oerp__.read(
                instance.__osv__['name'],
                [instance.id], [self.name])[0][self.name]
            instance.__data__['values'][self.name] = id_
        if id_:
            context = instance.__data__['context'].copy()
            context.update(self.context)
            return instance.__class__.__oerp__.browse(
                self.relation, id_[0], context)
        return False

    def __set__(self, instance, value):
        if isinstance(value, browse.BrowseRecord):
            o_rel = value
        elif is_int(value):
            o_rel = instance.__class__.__oerp__.browse(self.relation, value)
        elif value in [None, False]:
            o_rel = False
        else:
            raise ValueError("Value supplied has to be an integer, "
                             "a browse_record object or False.")
        o_rel = self.check_value(o_rel)
        instance.__data__['updated_values'][self.name] = \
            o_rel and [o_rel.id, False]

    def check_value(self, value):
        super(Many2OneField, self).check_value(value)
        if value and value.__osv__['name'] != self.relation:
            raise ValueError(
                ("Instance of '{model}' supplied doesn't match with the " +
                 "relation '{relation}' of the '{field_name}' field.").format(
                     model=value.__osv__['name'],
                     relation=self.relation,
                     field_name=self.name))
        return value


class One2ManyField(BaseField):
    """Represent the OpenObject 'fields.one2many'"""
    def __init__(self, osv, name, data):
        super(One2ManyField, self).__init__(osv, name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        """Return a generator to iterate on ``browse_record`` instances."""
        ids = None
        if instance.__data__['values'][self.name]:
            ids = instance.__data__['values'][self.name][:]
        # None value => get the value on the fly
        if ids is None:
            orig_ids = instance.__oerp__.read(
                instance.__osv__['name'],
                [instance.id], [self.name])[0][self.name]
            instance.__data__['values'][self.name] = orig_ids
            ids = orig_ids and orig_ids[:] or []
        # Take updated values into account
        if self.name in instance.__data__['updated_values']:
            ids = ids or []
            values = instance.__data__['updated_values'][self.name]
            # Handle OERP tuples to update 'ids'
            for value in values:
                if value[0] == 6 and value[2]:
                    ids = value[2]
                elif value[0] == 5:
                    ids = []
                elif value[0] == 4 and value[1] and value[1] not in ids:
                    ids.append(value[1])
                elif value[0] == 3 and value[1] and value[1] in ids:
                    ids.remove(value[1])
        context = instance.__data__['context'].copy()
        context.update(self.context)
        return browse.BrowseRecordIterator(
            model=instance.__oerp__.get(self.relation),
            ids=ids,
            context=context,
            parent=instance,
            parent_field=self)

    def __set__(self, instance, value):
        value = self.check_value(value)
        if value and not oerp_tuple_in(value):
            value = [(6, 0, records2ids(value))]
        elif not value:
            value = [(5, )]
        instance.__data__['updated_values'][self.name] = value

    def check_value(self, value):
        if value:
            if not isinstance(value, list):
                raise ValueError(
                    "The value supplied has to be a list or 'False'")
        return super(One2ManyField, self).check_value(value)


class ReferenceField(BaseField):
    """.. versionadded:: 0.6
    Represent the OpenObject 'fields.reference'.
    """
    def __init__(self, osv, name, data):
        super(ReferenceField, self).__init__(osv, name, data)
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False
        self.selection = 'selection' in data and data['selection'] or False

    def __get__(self, instance, owner):
        value = instance.__data__['values'][self.name]
        if self.name in instance.__data__['updated_values']:
            value = instance.__data__['updated_values'][self.name]
        # None value => get the value on the fly
        if value is None:
            value = instance.__oerp__.read(
                instance.__osv__['name'],
                [instance.id], [self.name])[0][self.name]
            instance.__data__['values'][self.name] = value
        if value:
            relation, sep, o_id = value.rpartition(',')
            relation = relation.strip()
            o_id = int(o_id.strip())
            if relation and o_id:
                context = instance.__data__['context'].copy()
                context.update(self.context)
                return instance.__class__.__oerp__.browse(
                    relation, o_id, context)
        return False

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance.__data__['updated_values'][self.name] = value

    def _check_relation(self, relation):
        selection = [val[0] for val in self.selection]
        if relation not in selection:
            raise ValueError(
                ("The value '{value}' supplied doesn't match with the possible"
                 " values '{selection}' for the '{field_name}' field").format(
                     value=relation,
                     selection=selection,
                     field_name=self.name,
                 ))
        return relation

    def check_value(self, value):
        if isinstance(value, browse.BrowseRecord):
            relation = value.__class__.__osv__['name']
            self._check_relation(relation)
            value = "%s,%s" % (relation, value.id)
            super(ReferenceField, self).check_value(value)
        elif isinstance(value, basestring):
            super(ReferenceField, self).check_value(value)
            relation, sep, o_id = value.rpartition(',')
            relation = relation.strip()
            o_id = o_id.strip()
            #o_rel = instance.__class__.__oerp__.browse(relation, o_id)
            if not relation or not is_int(o_id):
                raise ValueError("String not well formatted, expecting "
                                 "'{relation},{id}' format")
            self._check_relation(relation)
        else:
            raise ValueError("Value supplied has to be a string or"
                             " a browse_record object.")
        return value


class DateField(BaseField):
    """Represent the OpenObject 'fields.data'"""
    pattern = "%Y-%m-%d"

    def __init__(self, osv, name, data):
        super(DateField, self).__init__(osv, name, data)

    def __get__(self, instance, owner):
        value = instance.__data__['values'][self.name]
        if self.name in instance.__data__['updated_values']:
            value = instance.__data__['updated_values'][self.name]
        try:
            res = datetime.datetime.strptime(value, self.pattern).date()
        except Exception:  # ValueError, TypeError
            res = value
        return res

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance.__data__['updated_values'][self.name] = value

    def check_value(self, value):
        super(DateField, self).check_value(value)
        if isinstance(value, datetime.date):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, basestring):
            try:
                datetime.datetime.strptime(value, self.pattern)
            except:
                raise ValueError(
                    "String not well formatted, expecting '{0}' format".format(
                        self.pattern))
        elif isinstance(value, bool):
            return value
        else:
            raise ValueError(
                "Expecting a datetime.date object or basestring")
        return value


class DateTimeField(BaseField):
    """Represent the OpenObject 'fields.datetime'"""
    pattern = "%Y-%m-%d %H:%M:%S"

    def __init__(self, osv, name, data):
        super(DateTimeField, self).__init__(osv, name, data)

    def __get__(self, instance, owner):
        value = instance.__data__['values'][self.name]
        if self.name in instance.__data__['updated_values']:
            value = instance.__data__['updated_values'][self.name]
        try:
            res = datetime.datetime.strptime(value, self.pattern)
        except Exception:  # ValueError, TypeError
            res = value
        return res

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance.__data__['updated_values'][self.name] = value

    def check_value(self, value):
        super(DateTimeField, self).check_value(value)
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, basestring):
            try:
                datetime.datetime.strptime(value, self.pattern)
            except:
                raise ValueError(
                    "Value not well formatted, expecting '{0}' format".format(
                        self.pattern))
        elif isinstance(value, bool):
            return value
        else:
            raise ValueError(
                "Expecting a datetime.datetime object or basestring")
        return value


class ValueField(BaseField):
    """Represent simple OpenObject fields:
    - 'fields.char',
    - 'fields.float',
    - 'fields.integer',
    - 'fields.boolean',
    - 'fields.text',
    - 'fields.binary',
    """
    def __init__(self, osv, name, data):
        super(ValueField, self).__init__(osv, name, data)

    def __get__(self, instance, owner):
        if self.name in instance.__data__['updated_values']:
            return instance.__data__['updated_values'][self.name]
        return instance.__data__['values'][self.name]

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance.__data__['updated_values'][self.name] = value


def generate_field(osv, name, data):
    """Generate a well-typed field according to the data dictionary supplied
    (obtained via 'fields_get' XML-RPC/NET-RPC method).

    """
    assert 'type' in data
    field = None
    if data['type'] == 'selection':
        field = SelectionField(osv, name, data)
    elif data['type'] == 'many2many':
        field = Many2ManyField(osv, name, data)
    elif data['type'] == 'many2one':
        field = Many2OneField(osv, name, data)
    elif data['type'] == 'one2many':
        field = One2ManyField(osv, name, data)
    elif data['type'] == 'reference':
        field = ReferenceField(osv, name, data)
    elif data['type'] == 'date':
        field = DateField(osv, name, data)
    elif data['type'] == 'datetime':
        field = DateTimeField(osv, name, data)
    elif data['type'] in ['char', 'float', 'integer', 'integer_big',
                          'boolean', 'text', 'binary', 'html']:
        field = ValueField(osv, name, data)
    else:
        field = ValueField(osv, name, data)
    return field

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
