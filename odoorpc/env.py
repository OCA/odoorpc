# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""Supply the :class:`Environment` class to manage records more efficiently."""

import sys
import weakref

from odoorpc import fields
from odoorpc.models import Model
from odoorpc.tools import v

FIELDS_RESERVED = ['id', 'ids', '__odoo__', '__osv__', '__data__', 'env']


class Environment(object):
    """An environment wraps data like the user ID, context or current database
    name, and provides an access to data model proxies.

    .. doctest::
        :options: +SKIP

        >>> import odoorpc
        >>> odoo = odoorpc.ODOO('localhost')
        >>> odoo.login('db_name', 'admin', 'password')
        >>> odoo.env
        Environment(db='db_name', uid=1, context={'lang': 'fr_FR', 'tz': 'Europe/Brussels', 'uid': 1})

    .. doctest::
        :hide:

        >>> odoo.env
        Environment(db=..., uid=..., context=...)
    """

    def __init__(self, odoo, db, uid, context):
        self._odoo = odoo
        self._db = db
        self._uid = uid
        self._context = context
        self._registry = {}
        self._dirty = weakref.WeakSet()  # set of records updated locally

    def __repr__(self):
        return "Environment(db={}, uid={}, context={})".format(
            repr(self._db), self._uid, self._context
        )

    @property
    def dirty(self):
        """
        .. warning::

            This property is used internally and should not be used directly.
            As such, it should not be referenced in the user documentation.

        List records having local changes.
        These changes can be committed to the server with the :func:`commit`
        method, or invalidated with :func:`invalidate`.
        """
        return self._dirty

    @property
    def context(self):
        """The context of the user connected.

        .. doctest::
            :options: +SKIP

            >>> odoo.env.context
            {'lang': 'en_US', 'tz': 'Europe/Brussels', 'uid': 2}

        .. doctest::
            :hide:

            >>> from pprint import pprint as pp
            >>> pp(odoo.env.context)
            {'lang': 'en_US', 'tz': 'Europe/Brussels', 'uid': ...}
        """
        return self._context

    @property
    def db(self):
        """The database currently used.

        .. doctest::
            :options: +SKIP

            >>> odoo.env.db
            'db_name'

        .. doctest::
            :hide:

            >>> odoo.env.db == DB
            True
        """
        return self._db

    def commit(self):
        """Commit dirty records to the server. This method is automatically
        called when the `auto_commit` option is set to `True` (default).
        It can be useful to set the former option to `False` to get better
        performance by reducing the number of RPC requests generated.

        With `auto_commit` set to `True` (default behaviour), each time a value
        is set on a record field a RPC request is sent to the server to update
        the record:

        .. doctest::

            >>> user = odoo.env.user
            >>> user.name = "Joe"               # write({'name': "Joe"})
            >>> user.email = "joe@odoo.net"     # write({'email': "joe@odoo.net"})

        With `auto_commit` set to `False`, changes on a record are sent all at
        once when calling the :func:`commit` method:

        .. doctest::

            >>> odoo.config['auto_commit'] = False
            >>> user = odoo.env.user
            >>> user.name = "Joe"
            >>> user.email = "joe@odoo.net"
            >>> user in odoo.env.dirty
            True
            >>> odoo.env.commit()   # write({'name': "Joe", 'email': "joe@odoo.net"})
            >>> user in odoo.env.dirty
            False

        Only one RPC request is generated in the last case.
        """
        # Iterate on a new set, as we remove record during iteration from the
        # original one
        for record in set(self.dirty):
            values = {}
            for field in record._values_to_write:
                if record.id in record._values_to_write[field]:
                    value = record._values_to_write[field].pop(record.id)
                    values[field] = value
                    # Store the value in the '_values' dictionary. This
                    # operation is delegated to each field descriptor as some
                    # values can not be stored "as is" (e.g. magic tuples of
                    # 2many fields need to be converted)
                    record.__class__.__dict__[field].store(record, value)
            record.write(values)
            self.dirty.remove(record)

    def invalidate(self):
        """Invalidate the cache of records."""
        self.dirty.clear()

    @property
    def lang(self):
        """Return the current language code.

        .. doctest::

            >>> odoo.env.lang
            'en_US'
        """
        return self.context.get('lang', False)

    def ref(self, xml_id):
        """Return the record corresponding to the given `xml_id` (also called
        external ID).
        Raise an :class:`RPCError <odoorpc.error.RPCError>` if no record
        is found.

        .. doctest::

            >>> odoo.env.ref('base.lang_en')
            Recordset('res.lang', [1])

        :return: a :class:`odoorpc.models.Model` instance (recordset)
        :raise: :class:`odoorpc.error.RPCError`
        """
        if v(self._odoo.version)[0] < 15:
            model, id_ = self._odoo.execute(
                "ir.model.data", "xmlid_to_res_model_res_id", xml_id, True
            )
        module, name = xml_id.split(".", 1)
        model, id_ = self._odoo.execute(
            "ir.model.data", "check_object_reference", module, name, True
        )
        return self[model].browse(id_)

    @property
    def uid(self):
        """The user ID currently logged.

        .. doctest::
            :options: +SKIP

            >>> odoo.env.uid
            1

        .. doctest::
            :hide:

            >>> odoo.env.uid in [1, 2]
            True
        """
        return self._uid

    @property
    def user(self):
        """Return the current user (as a record).

        .. doctest::
            :options: +SKIP

            >>> user = odoo.env.user
            >>> user
            Recordset('res.users', [2])
            >>> user.name
            'Mitchell Admin'

        .. doctest::
            :hide:

            >>> user = odoo.env.user
            >>> user.id in [1, 2]
            True
            >>> 'Admin' in user.name
            True

        :return: a :class:`odoorpc.models.Model` instance
        :raise: :class:`odoorpc.error.RPCError`
        """
        return self['res.users'].browse(self.uid)

    @property
    def registry(self):
        """The data model registry. It is a mapping between a model name and
        its corresponding proxy used to generate records.
        As soon as a model is needed the proxy is added to the registry. This
        way the model proxy is ready for a further use (avoiding costly `RPC`
        queries when browsing records through relations).

        .. doctest::
            :hide:

            >>> odoo.env.registry.clear()

        >>> odoo.env.registry
        {}
        >>> odoo.env.user.company_id.name   # 'res.users' and 'res.company' Model proxies will be fetched
        'YourCompany'
        >>> from pprint import pprint
        >>> pprint(odoo.env.registry)
        {'res.company': Model('res.company'), 'res.users': Model('res.users')}

        If you need to regenerate the model proxy, simply delete it from the
        registry:

        >>> del odoo.env.registry['res.company']

        To delete all model proxies:

        >>> odoo.env.registry.clear()
        >>> odoo.env.registry
        {}
        """
        return self._registry

    def __getitem__(self, model):
        """Return the model class corresponding to `model`.

        >>> Partner = odoo.env['res.partner']
        >>> Partner
        Model('res.partner')

        :return: a :class:`odoorpc.models.Model` class
        """
        if model not in self.registry:
            # self.registry[model] = Model(self._odoo, self, model)
            self.registry[model] = self._create_model_class(model)
        return self.registry[model]

    def __call__(self, context=None):
        """Return an environment based on `self` with a different
        user context.
        """
        context = self.context if context is None else context
        env = Environment(self._odoo, self._db, self._uid, context)
        env._dirty = self._dirty
        env._registry = self._registry
        return env

    def __contains__(self, model):
        """Check if the given `model` exists on the server.

        >>> 'res.partner' in odoo.env
        True

        :return: `True` or `False`
        """
        model_exists = self._odoo.execute(
            'ir.model', 'search', [('model', '=', model)]
        )
        return bool(model_exists)

    def _create_model_class(self, model):
        """Generate the model proxy class.

        :return: a :class:`odoorpc.models.Model` class
        """
        cls_name = model.replace('.', '_')
        # Hack for Python 2 (no need to do this for Python 3)
        if sys.version_info[0] < 3:
            # noqa: F821
            if isinstance(cls_name, unicode):  # noqa: F821
                cls_name = cls_name.encode('utf-8')
        # Retrieve server fields info and generate corresponding local fields
        attrs = {
            '_env': self,
            '_odoo': self._odoo,
            '_name': model,
            '_columns': {},
        }
        fields_get = self._odoo.execute(model, 'fields_get')
        for field_name, field_data in fields_get.items():
            if field_name not in FIELDS_RESERVED:
                Field = fields.generate_field(field_name, field_data)
                attrs['_columns'][field_name] = Field
                attrs[field_name] = Field
        return type(cls_name, (Model,), attrs)
