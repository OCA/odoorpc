# -*- coding: UTF-8 -*-
##############################################################################
#
#    OdooRPC
#    Copyright (C) 2014 Sébastien Alix.
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
"""Provide the :class:`Model` class which allow to access dynamically to all
methods proposed by a data model."""

import sys  # to check Python version at runtime
import collections

from odoorpc.tools import v
from odoorpc import error
from odoorpc.service.osv import fields, browse


class Model(object):
    """.. versionadded:: 0.5

    Represent a data model.

    .. note::
        This class have to be used through the :func:`odoorpc.OERP.get`
        method.

    >>> import odoorpc
    >>> oerp = odoorpc.OERP('localhost')
    >>> user = oerp.login('admin', 'passwd', 'database')
    >>> user_obj = oerp.get('res.users')
    >>> user_obj
    <odoorpc.service.osv.osv.Model object at 0xb75ba4ac>
    >>> user_obj.name_get(user.id) # Use any methods from the model instance
    [[1, 'Administrator']]

    .. warning::

        The only method implemented in this class is ``browse``. Except this
        one, method calls are purely dynamic. As long as you know the signature
        of the model method targeted, you will be able to use it
        (see the :ref:`tutorial <tutorials-execute-queries>`).

    """

    fields_reserved = ['id', '__oerp__', '__osv__', '__data__']

    def __init__(self, oerp, model):
        super(Model, self).__init__()
        self._oerp = oerp
        self._name = model
        self._browse_class = self._generate_browse_class()

    def browse(self, ids, context=None):
        """Browse one or several records (if `ids` is a list of IDs)
        from `model`. The fields and values for such objects are generated
        dynamically.

        >>> oerp.get('res.partner').browse(1)
        browse_record(res.partner, 1)

        >>> [partner.name for partner in oerp.get('res.partner').browse([1, 2])]
        [u'Your Company', u'ASUStek']

        A list of data types used by ``browse_record`` fields are
        available :ref:`here <fields>`.

        :return: a ``browse_record`` instance
        :return: a generator to iterate on ``browse_record`` instances
        :raise: :class:`odoorpc.error.RPCError`

        """
        if isinstance(ids, list):
            return browse.BrowseRecordIterator(self, ids, context=context)
            #return browse.BrowseRecordIterator(
            #    model=self,
            #    ids=ids,
            #    context=context)
        else:
            obj = self._browse_class(ids)
            self._refresh(obj, context)
            return obj
            #return self.browse(ids, context)

    def _generate_browse_class(self):
        """Generate a class with all its fields corresponding to
        the model name supplied and return them.

        """
        # Retrieve server fields info and generate corresponding local fields
        fields_get = self._oerp.execute(self._name, 'fields_get')
        cls_name = self._name.replace('.', '_')
        # Encode the class name for the Python2 'type()' function.
        # No need to do this for Python3.
        if type(cls_name) == unicode and sys.version_info < (3,):
            cls_name = cls_name.encode('utf-8')
        cls_fields = {}
        for field_name, field_data in fields_get.items():
            if field_name not in Model.fields_reserved:
                cls_fields[field_name] = fields.generate_field(
                    self, field_name, field_data)
        # Case where no field 'name' exists, we generate one (which will be
        # in readonly mode) in purpose to be filled with the 'name_get' method
        if 'name' not in cls_fields:
            field_data = {'type': 'text', 'string': 'Name', 'readonly': True}
            cls_fields['name'] = fields.generate_field(self, 'name', field_data)

        cls = type(cls_name, (browse.BrowseRecord,), {})
        cls.__oerp__ = self._oerp
        cls.__osv__ = {'name': self._name, 'columns': cls_fields}
        slots = ['__oerp__', '__osv__', '__dict__', '__data__']
        slots.extend(cls_fields.keys())
        cls.__slots__ = slots
        return cls

    def _write_record(self, obj, context=None):
        """Send values of fields updated to the server."""
        obj_data = obj.__data__
        vals = {}
        for field_name in obj_data['updated_values']:
            if field_name in obj_data['raw_data']:
                field = self._browse_class.__osv__['columns'][field_name]
                field_value = obj.__data__['updated_values'][field_name]
                # Many2One fields
                if isinstance(field, fields.Many2OneField):
                    vals[field_name] = field_value and field_value[0]
                # All other fields
                else:
                    vals[field_name] = field_value
        try:
            if v(self._oerp.version) < v('6.1'):
                res = self.write([obj.id], vals, context)
            else:
                res = self.write([obj.id], vals, context=context)
        except error.Error as exc:
            raise exc
        else:
            # Update raw_data dictionary
            # FIXME: make it optional to avoid a RPC request?
            self._refresh(obj, context)
            return res

    def _refresh(self, obj, context=None):
        """Retrieve field values from the server.
        May be used to restore the original values
        in the purpose to cancel all changes made.

        """
        context = context or self._oerp.context
        obj_data = obj.__data__
        obj_data['context'] = context
        # Get basic fields (no relational ones)
        basic_fields = []
        for field_name, field in obj.__osv__['columns'].iteritems():
            if not getattr(field, 'relation', False):
                basic_fields.append(field_name)
            else:
                obj_data['raw_data'][field_name] = None
        # Fill fields with values of the record
        if obj.id:
            if v(self._oerp.version) < v('6.1'):
                data = self.read([obj.id], basic_fields, context)
                if data:
                    obj_data['raw_data'].update(data[0])
                else:
                    obj_data['raw_data'] = False
            else:
                data = self.read([obj.id], basic_fields, context=context)
                if data:
                    obj_data['raw_data'].update(data[0])
                else:
                    obj_data['raw_data'] = False
            if obj_data['raw_data'] is False:
                raise error.RPCError(
                    "There is no '{model}' record with ID {obj_id}.".format(
                        model=obj.__class__.__osv__['name'], obj_id=obj.id))
        # No ID: fields filled with default values
        else:
            if v(self._oerp.version) < v('6.1'):
                default_get = self.default_get(
                    obj.__osv__['columns'].keys(), context)
            else:
                default_get = self.default_get(
                    obj.__osv__['columns'].keys(), context=context)
            obj_data['raw_data'] = {}
            for field_name in obj.__osv__['columns']:
                obj_data['raw_data'][field_name] = False
            obj_data['raw_data'].update(default_get)
        self._reset(obj)

    def _reset(self, obj):
        """Cancel all changes by restoring field values with original values
        obtained during the last refresh (object instanciation or
        last call to _refresh() method).

        """
        obj_data = obj.__data__
        obj_data['updated_values'] = {}
        # Load fields and their values
        for field in self._browse_class.__osv__['columns'].values():
            if field.name in obj_data['raw_data']:
                obj_data['values'][field.name] = \
                    obj_data['raw_data'][field.name]
                setattr(obj.__class__, field.name, field)

    def _unlink_record(self, obj, context=None):
        """Delete the object from the server."""
        if v(self._oerp.version) < v('6.1'):
            return self.unlink([obj.id], context)
        else:
            return self.unlink([obj.id], context=context)

    def __getattr__(self, method):
        """Provide a dynamic access to a RPC method."""
        def rpc_method(*args, **kwargs):
            """Return the result of the RPC request."""
            if v(self._oerp.version) < v('6.1'):
                if kwargs:
                    raise error.RPCError(
                        "Named parameters are not supported by the version "
                        "of this server.")
                result = self._oerp.execute(
                    self._browse_class.__osv__['name'], method, *args)
            else:
                if self._oerp.config['auto_context'] \
                        and 'context' not in kwargs:
                    kwargs['context'] = self._oerp.context
                result = self._oerp.execute_kw(
                    self._browse_class.__osv__['name'], method, args, kwargs)
            return result
        return rpc_method

    def __repr__(self):
        return "Model(%r)" % (self._browse_class.__osv__['name'])

    # ---------------------------- #
    # -- MutableMapping methods -- #
    # ---------------------------- #

    def __getitem__(self, obj_id):
        return self.browse(obj_id)

    def __iter__(self):
        ids = self.search([])
        return browse.BrowseRecordIterator(self, ids)

    def __len__(self):
        return self._oerp.search(self._browse_class.__osv__['name'], count=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
