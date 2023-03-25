# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""This module contains classes representing the fields supported by Odoo.
A field is a Python descriptor which defines getter/setter methods for
its related attribute.
"""
import datetime
import sys

# from odoorpc import error
from odoorpc.models import IncrementalRecords, Model


def is_int(value):
    """Return `True` if ``value`` is an integer."""
    if isinstance(value, bool):
        return False
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


# Python 2
if sys.version_info[0] < 3:

    def is_string(value):
        """Return `True` if ``value`` is a string."""
        # noqa: F821
        return isinstance(value, basestring)  # noqa: F821


# Python >= 3
else:

    def is_string(value):
        """Return `True` if ``value`` is a string."""
        return isinstance(value, str)


def odoo_tuple_in(iterable):
    """Return `True` if `iterable` contains an expected tuple like
    ``(6, 0, IDS)`` (and so on).

        >>> odoo_tuple_in([0, 1, 2])        # Simple list
        False
        >>> odoo_tuple_in([(6, 0, [42])])   # List of tuples
        True
        >>> odoo_tuple_in([[1, 42]])        # List of lists
        True
    """
    if not iterable:
        return False

    def is_odoo_tuple(elt):
        """Return `True` if `elt` is a Odoo special tuple."""
        try:
            return elt[:1][0] in [1, 2, 3, 4, 5] or elt[:2] in [
                (6, 0),
                [6, 0],
                (0, 0),
                [0, 0],
            ]
        except (TypeError, IndexError):
            return False

    return any(is_odoo_tuple(elt) for elt in iterable)


def tuples2ids(tuples, ids):
    """Update `ids` according to `tuples`, e.g. (3, 0, X), (4, 0, X)..."""
    for value in tuples:
        if value[0] == 6 and value[2]:
            ids = value[2]
        elif value[0] == 5:
            ids[:] = []
        elif value[0] == 4 and value[1] and value[1] not in ids:
            ids.append(value[1])
        elif value[0] == 3 and value[1] and value[1] in ids:
            ids.remove(value[1])
    return ids


def records2ids(iterable):
    """Replace records contained in `iterable` with their corresponding IDs:

        >>> groups = list(odoo.env.user.groups_id)
        >>> records2ids(groups)
        [1, 2, 3, 14, 17, 18, 19, 7, 8, 9, 5, 20, 21, 22, 23]
    """

    def record2id(elt):
        """If `elt` is a record, return its ID."""
        if isinstance(elt, Model):
            return elt.id
        return elt

    return [record2id(elt) for elt in iterable]


class BaseField(object):
    """Field which all other fields inherit.
    Manage common metadata.
    """

    def __init__(self, name, data):
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
        """Each time a record is modified, it is marked as dirty
        in the environment.
        """
        instance.env.dirty.add(instance)
        if instance._odoo.config.get('auto_commit'):
            instance.env.commit()

    def __str__(self):
        """Return a human readable string representation of the field."""
        attrs = [
            'string',
            'relation',
            'required',
            'readonly',
            'size',
            'domain',
        ]
        attrs_rep = []
        for attr in attrs:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if value:
                    if is_string(value):
                        attrs_rep.append("{}='{}'".format(attr, value))
                    else:
                        attrs_rep.append("{}={}".format(attr, value))
        attrs_rep = ", ".join(attrs_rep)
        return "{}({})".format(self.type, attrs_rep)

    def check_required(self, value):
        """Check the value if the field is required.

        Aim to be overridden by field classes.

        :return: `True` if the value is accepted, `False` otherwise.
        """
        return bool(value)

    def check_value(self, value):
        """Check the validity of a value for the field."""
        # if self.readonly:
        #    raise error.Error(
        #        "'{field_name}' field is readonly".format(
        #            field_name=self.name))
        if value and self.size:
            if not is_string(value):
                raise ValueError("Value supplied has to be a string")
            if len(value) > self.size:
                raise ValueError(
                    "Lenght of the '{}' is limited to {}".format(
                        self.name, self.size
                    )
                )
        if self.required and not self.check_required(value):
            raise ValueError("'{}' field is required".format(self.name))
        return value

    def store(self, record, value):
        """Store the value in the record."""
        record._values[self.name][record.id] = value


class Binary(BaseField):
    """Equivalent of the `fields.Binary` class."""

    def __init__(self, name, data):
        super(Binary, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name][instance.id]
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        if value is None:
            value = False
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Binary, self).__set__(instance, value)


class Boolean(BaseField):
    """Equivalent of the `fields.Boolean` class."""

    def __init__(self, name, data):
        super(Boolean, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name][instance.id]
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        value = bool(value)
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Boolean, self).__set__(instance, value)


class Char(BaseField):
    """Equivalent of the `fields.Char` class."""

    def __init__(self, name, data):
        super(Char, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        if value is None:
            value = False
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Char, self).__set__(instance, value)


class Date(BaseField):
    """Represent the OpenObject 'fields.data'"""

    pattern = "%Y-%m-%d"

    def __init__(self, name, data):
        super(Date, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id) or False
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        try:
            res = datetime.datetime.strptime(value, self.pattern).date()
        except (ValueError, TypeError):
            res = value
        return res

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Date, self).__set__(instance, value)

    def check_value(self, value):
        super(Date, self).check_value(value)
        if isinstance(value, datetime.date):
            value = value.strftime("%Y-%m-%d")
        elif is_string(value):
            datetime.datetime.strptime(value, self.pattern)
        elif isinstance(value, bool) or value is None:
            return value
        else:
            raise ValueError("Expecting a datetime.date object or string")
        return value


class Datetime(BaseField):
    """Represent the OpenObject 'fields.datetime'"""

    pattern = "%Y-%m-%d %H:%M:%S"

    def __init__(self, name, data):
        super(Datetime, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        try:
            res = datetime.datetime.strptime(value, self.pattern)
        except (ValueError, TypeError):
            res = value
        return res

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Datetime, self).__set__(instance, value)

    def check_value(self, value):
        super(Datetime, self).check_value(value)
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        elif is_string(value):
            datetime.datetime.strptime(value, self.pattern)
        elif isinstance(value, bool):
            return value
        else:
            raise ValueError("Expecting a datetime.datetime object or string")
        return value


class Float(BaseField):
    """Equivalent of the `fields.Float` class."""

    def __init__(self, name, data):
        super(Float, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        if value in [None, False]:
            value = 0.0
        return value

    def __set__(self, instance, value):
        if value is None:
            value = False
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Float, self).__set__(instance, value)

    def check_required(self, value):
        # Accept 0 values
        return super(Float, self).check_required() or value == 0


class Integer(BaseField):
    """Equivalent of the `fields.Integer` class."""

    def __init__(self, name, data):
        super(Integer, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        if value in [None, False]:
            value = 0
        return value

    def __set__(self, instance, value):
        if value is None:
            value = False
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Integer, self).__set__(instance, value)

    def check_required(self, value):
        # Accept 0 values
        return super(Float, self).check_required() or value == 0


class Selection(BaseField):
    """Represent the OpenObject 'fields.selection'"""

    def __init__(self, name, data):
        super(Selection, self).__init__(name, data)
        self.selection = 'selection' in data and data['selection'] or False

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id, False)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        if value is None:
            value = False
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Selection, self).__set__(instance, value)

    def check_value(self, value):
        super(Selection, self).check_value(value)
        selection = [val[0] for val in self.selection]
        if value and value not in selection:
            raise ValueError(
                "The value '{}' supplied doesn't match with the possible "
                "values '{}' for the '{}' field".format(
                    value, selection, self.name
                )
            )
        return value


class Many2many(BaseField):
    """Represent the OpenObject 'fields.many2many'"""

    def __init__(self, name, data):
        super(Many2many, self).__init__(name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        """Return a recordset."""
        ids = None
        if instance._values[self.name].get(instance.id):
            ids = instance._values[self.name][instance.id][:]
        # None value => get the value on the fly
        if ids is None:
            args = [[instance.id], [self.name]]
            kwargs = {'context': self.context, 'load': '_classic_write'}
            orig_ids = instance._odoo.execute_kw(
                instance._name, 'read', args, kwargs
            )[0][self.name]
            instance._values[self.name][instance.id] = orig_ids
            ids = orig_ids and orig_ids[:] or []
        # Take updated values into account
        if instance.id in instance._values_to_write[self.name]:
            values = instance._values_to_write[self.name][instance.id]
            # Handle ODOO tuples to update 'ids'
            ids = tuples2ids(values, ids or [])
        # Handle the field context
        Relation = instance.env[self.relation]
        env = instance.env
        if self.context:
            context = instance.env.context.copy()
            context.update(self.context)
            env = instance.env(context=context)
        return Relation._browse(env, ids, from_record=(instance, self))

    def __set__(self, instance, value):
        value = self.check_value(value)
        if isinstance(value, IncrementalRecords):
            value = value.tuples
        else:
            if value and not odoo_tuple_in(value):
                value = [(6, 0, records2ids(value))]
            elif not value:
                value = [(5,)]
        instance._values_to_write[self.name][instance.id] = value
        super(Many2many, self).__set__(instance, value)

    def check_value(self, value):
        if value:
            if (
                not isinstance(value, list)
                and not isinstance(value, Model)
                and not isinstance(value, IncrementalRecords)
            ):
                raise ValueError(
                    "The value supplied has to be a list, a recordset "
                    "or 'False'"
                )
        return super(Many2many, self).check_value(value)

    def store(self, record, value):
        """Store the value in the record."""
        if record._values[self.name].get(record.id):
            tuples2ids(value, record._values[self.name][record.id])
        else:
            record._values[self.name][record.id] = tuples2ids(value, [])


class Many2one(BaseField):
    """Represent the OpenObject 'fields.many2one'"""

    def __init__(self, name, data):
        super(Many2one, self).__init__(name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        id_ = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            id_ = instance._values_to_write[self.name][instance.id]
        # None value => get the value on the fly
        if id_ is None:
            args = [[instance.id], [self.name]]
            kwargs = {'context': self.context, 'load': '_classic_write'}
            id_ = instance._odoo.execute_kw(
                instance._name, 'read', args, kwargs
            )[0][self.name]
            instance._values[self.name][instance.id] = id_
        Relation = instance.env[self.relation]
        if id_:
            env = instance.env
            if self.context:
                context = instance.env.context.copy()
                context.update(self.context)
                env = instance.env(context=context)
            return Relation._browse(env, id_, from_record=(instance, self))
        return Relation.browse(False)

    def __set__(self, instance, value):
        if isinstance(value, Model):
            o_rel = value
        elif is_int(value):
            rel_obj = instance.env[self.relation]
            o_rel = rel_obj.browse(value)
        elif value in [None, False]:
            o_rel = False
        else:
            raise ValueError(
                "Value supplied has to be an integer, "
                "a record object or 'None/False'."
            )
        o_rel = self.check_value(o_rel)
        # instance.__data__['updated_values'][self.name] = \
        #    o_rel and [o_rel.id, False]
        instance._values_to_write[self.name][instance.id] = (
            o_rel and o_rel.id or False
        )
        super(Many2one, self).__set__(instance, value)

    def check_value(self, value):
        super(Many2one, self).check_value(value)
        if value and value._name != self.relation:
            raise ValueError(
                (
                    "Instance of '{model}' supplied doesn't match with the "
                    + "relation '{relation}' of the '{field_name}' field."
                ).format(
                    model=value._name,
                    relation=self.relation,
                    field_name=self.name,
                )
            )
        return value


class One2many(BaseField):
    """Represent the OpenObject 'fields.one2many'"""

    def __init__(self, name, data):
        super(One2many, self).__init__(name, data)
        self.relation = 'relation' in data and data['relation'] or False
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False

    def __get__(self, instance, owner):
        """Return a recordset."""
        ids = None
        if instance._values[self.name].get(instance.id):
            ids = instance._values[self.name][instance.id][:]
        # None value => get the value on the fly
        if ids is None:
            args = [[instance.id], [self.name]]
            kwargs = {'context': self.context, 'load': '_classic_write'}
            orig_ids = instance._odoo.execute_kw(
                instance._name, 'read', args, kwargs
            )[0][self.name]
            instance._values[self.name][instance.id] = orig_ids
            ids = orig_ids and orig_ids[:] or []
        # Take updated values into account
        if instance.id in instance._values_to_write[self.name]:
            values = instance._values_to_write[self.name][instance.id]
            # Handle ODOO tuples to update 'ids'
            ids = tuples2ids(values, ids or [])
        Relation = instance.env[self.relation]
        env = instance.env
        if self.context:
            context = instance.env.context.copy()
            context.update(self.context)
            env = instance.env(context=context)
        return Relation._browse(env, ids, from_record=(instance, self))

    def __set__(self, instance, value):
        value = self.check_value(value)
        if isinstance(value, IncrementalRecords):
            value = value.tuples
        else:
            if value and not odoo_tuple_in(value):
                value = [(6, 0, records2ids(value))]
            elif not value:
                value = [(5,)]
        instance._values_to_write[self.name][instance.id] = value
        super(One2many, self).__set__(instance, value)

    def check_value(self, value):
        if value:
            if (
                not isinstance(value, list)
                and not isinstance(value, Model)
                and not isinstance(value, IncrementalRecords)
            ):
                raise ValueError(
                    "The value supplied has to be a list, a recordset "
                    "or 'False'"
                )
        return super(One2many, self).check_value(value)

    def store(self, record, value):
        """Store the value in the record."""
        if record._values[self.name].get(record.id):
            tuples2ids(value, record._values[self.name][record.id])
        else:
            record._values[self.name][record.id] = tuples2ids(value, [])


class Reference(BaseField):
    """Represent the OpenObject 'fields.reference'."""

    def __init__(self, name, data):
        super(Reference, self).__init__(name, data)
        self.context = 'context' in data and data['context'] or {}
        self.domain = 'domain' in data and data['domain'] or False
        self.selection = 'selection' in data and data['selection'] or False

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id) or False
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        # None value => get the value on the fly
        if value is None:
            args = [[instance.id], [self.name]]
            kwargs = {'context': self.context, 'load': '_classic_write'}
            value = instance._odoo.execute_kw(
                instance._name, 'read', args, kwargs
            )[0][self.name]
            instance._values_to_write[self.name][instance.id] = value
        if value:
            parts = value.rpartition(',')
            relation, o_id = parts[0], parts[2]
            relation = relation.strip()
            o_id = int(o_id.strip())
            if relation and o_id:
                Relation = instance.env[relation]
                env = instance.env
                if self.context:
                    context = instance.env.context.copy()
                    context.update(self.context)
                    env = instance.env(context=context)
                return Relation._browse(
                    env, o_id, from_record=(instance, self)
                )
        return False

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Reference, self).__set__(instance, value)

    def _check_relation(self, relation):
        """Raise a `ValueError` if `relation` is not allowed among
        the possible values.
        """
        selection = [val[0] for val in self.selection]
        if relation not in selection:
            raise ValueError(
                (
                    "The value '{value}' supplied doesn't match with the possible"
                    " values '{selection}' for the '{field_name}' field"
                ).format(
                    value=relation, selection=selection, field_name=self.name
                )
            )
        return relation

    def check_value(self, value):
        if isinstance(value, Model):
            relation = value.__class__.__osv__['name']
            self._check_relation(relation)
            value = "{},{}".format(relation, value.id)
            super(Reference, self).check_value(value)
        elif is_string(value):
            super(Reference, self).check_value(value)
            parts = value.rpartition(',')
            relation, o_id = parts[0], parts[2]
            relation = relation.strip()
            o_id = o_id.strip()
            # o_rel = instance.__class__.__odoo__.browse(relation, o_id)
            if not relation or not is_int(o_id):
                raise ValueError(
                    "String not well formatted, expecting "
                    "'{relation},{id}' format"
                )
            self._check_relation(relation)
        else:
            raise ValueError(
                "Value supplied has to be a string or"
                " a browse_record object."
            )
        return value


class Text(BaseField):
    """Equivalent of the `fields.Text` class."""

    def __init__(self, name, data):
        super(Text, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        if value is None:
            value = False
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Text, self).__set__(instance, value)


class Html(Text):
    """Equivalent of the `fields.Html` class."""

    def __init__(self, name, data):
        super(Html, self).__init__(name, data)


class Unknown(BaseField):
    """Represent an unknown field. This should not happen but this kind of
    field only exists to avoid a blocking situation from a RPC point of view.
    """

    def __init__(self, name, data):
        super(Unknown, self).__init__(name, data)

    def __get__(self, instance, owner):
        value = instance._values[self.name][instance.id]
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        value = self.check_value(value)
        instance._values_to_write[self.name][instance.id] = value
        super(Unknown, self).__set__(instance, value)


TYPES_TO_FIELDS = {
    'binary': Binary,
    'boolean': Boolean,
    'char': Char,
    'date': Date,
    'datetime': Datetime,
    'float': Float,
    'html': Html,
    'integer': Integer,
    'many2many': Many2many,
    'many2one': Many2one,
    'one2many': One2many,
    'reference': Reference,
    'selection': Selection,
    'text': Text,
}


def generate_field(name, data):
    """Generate a well-typed field according to the data dictionary supplied
    (obtained via the `fields_get' method of any models).
    """
    assert 'type' in data
    field = TYPES_TO_FIELDS.get(data['type'], Unknown)(name, data)
    return field
