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
"""This module contains the ``OERP`` class which is the entry point to manage 
an `OpenERP/Odoo` server.
"""
import os
import base64
import zlib
import tempfile
import time

from oerplib import rpc, error, tools
from oerplib.tools import session
from oerplib.service import common, db, wizard, osv, inspect


class OERP(object):
    """Return a new instance of the :class:`OERP` class.
    The optional `database` parameter specifies the default database to use
    when the :func:`login <oerplib.OERP.login>` method is called.
    If no `database` is set, the `database` parameter of the
    :func:`login <oerplib.OERP.login>` method will be mandatory.

    `XML-RPC` and `Net-RPC` protocols are supported. Respective values for the
    `protocol` parameter are ``xmlrpc``, ``xmlrpc+ssl`` and ``netrpc``.

        >>> import oerplib
        >>> oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)

    Since the version `0.7`, `OERPLib` will try by default to detect the
    server version in order to adapt its requests. However, it is
    possible to force the version to use with the `version` parameter:

        >>> oerp = oerplib.OERP('localhost', version='6.0')

    :raise: :class:`oerplib.error.InternalError`,
        :class:`oerplib.error.RPCError`
    """

    def __init__(self, server='localhost', database=None, protocol='xmlrpc',
                 port=8069, timeout=120, version=None):
        if protocol not in ['xmlrpc', 'xmlrpc+ssl', 'netrpc']:
            txt = ("The protocol '{0}' is not supported by the OERP class. "
                   "Please choose a protocol among these ones: {1}")
            txt = txt.format(protocol, ['xmlrpc', 'xmlrpc+ssl', 'netrpc'])
            raise error.InternalError(txt)
        self._server = server
        self._port = port
        self._protocol = protocol
        self._database = self._database_default = database
        self._uid = None
        self._password = None
        self._user = None
        self._common = common.Common(self)
        self._db = db.DB(self)
        self._wizard = wizard.Wizard(self)
        self._inspect = inspect.Inspect(self)
        # Instanciate the server connector
        try:
            self._connector = rpc.PROTOCOLS[protocol](
                self._server, self._port, timeout, version)
        except rpc.error.ConnectorError as exc:
            raise error.InternalError(exc.message)
        # Dictionary of configuration options
        self._config = tools.Config(
            self,
            {'auto_context': True,
             'timeout': timeout})

    @property
    def config(self):
        """Dictionary of available configuration options.

        >>> oerp.config
        {'auto_context': True, 'timeout': 120}

        - ``auto_context``: if set to `True`, the user context will be sent
          automatically to every call of a
          :class:`model <oerplib.service.osv.Model>` method (default: `True`):

            .. versionadded:: 0.7

            .. note::

                This option only works on servers in version `6.1` and above.

            >>> product_osv = oerp.get('product.product')
            >>> product_osv.name_get([3]) # Context sent by default ('lang': 'fr_FR' here)
            [[3, '[PC1] PC Basic']]
            >>> oerp.config['auto_context'] = False
            >>> product_osv.name_get([3]) # No context sent
            [[3, '[PC1] Basic PC']]

        - ``timeout``: set the maximum timeout in seconds for a RPC request
          (default: `120`):

            .. versionadded:: 0.6

            >>> oerp.config['timeout'] = 300

        """
        return self._config

    # Readonly properties
    @property
    def user(self):
        """The browsable record of the user connected.

        >>> oerp.login('admin', 'admin') == oerp.user
        True

        """
        return self._user

    @property
    def context(self):
        """The context of the user connected.

        >>> oerp.login('admin', 'admin')
        browse_record('res.users', 1)
        >>> oerp.context
        {'lang': 'fr_FR', 'tz': False}
        >>> oerp.context['lang'] = 'en_US'

        """
        return self._context

    @property
    def version(self):
        """The version of the server.

        >>> oerp.version
        '7.0-20131014-231047'
        """
        return self._connector.version

    server = property(lambda self: self._server,
                      doc="The server name.")
    port = property(lambda self: self._port,
                    doc="The port used.")
    protocol = property(lambda self: self._protocol,
                        doc="The protocol used.")

    database = property(lambda self: self._database,
                        doc="The database currently used.")
    common = property(lambda self: self._common,
                      doc=(""".. versionadded:: 0.6

                       The common service (``/common`` RPC service).
                       See the :class:`oerplib.service.common.Common` class."""))
    db = property(lambda self: self._db,
                  doc=(""".. versionadded:: 0.4

                       The database management service (``/db`` RPC service).
                       See the :class:`oerplib.service.db.DB` class."""))
    wizard = property(lambda self: self._wizard,
                      doc=(""".. versionadded:: 0.6

                       The wizard service (``/wizard`` RPC service).
                       See the :class:`oerplib.service.wizard.Wizard` class."""))

    inspect = property(lambda self: self._inspect,
                       doc=(""".. versionadded:: 0.8

                       The inspect service (custom service).
                       See the :class:`oerplib.service.inspect.Inspect`
                       class."""))

    #NOTE: in the past this function was implemented as a decorator for other
    # methods needed to be checked, but Sphinx documentation generator is not
    # able to auto-document decorated methods.
    def _check_logged_user(self):
        """Check if a user is logged. Otherwise, an error is raised."""
        if not self._uid or not self._password:
            raise error.Error(u"User login required.")

    def login(self, user='admin', passwd='admin', database=None):
        """Log in as the given `user` with the password `passwd` on the
        database `database` and return the corresponding user as a browsable
        record (from the ``res.users`` model).
        If `database` is not specified, the default one will be used instead.

        >>> user = oerp.login('admin', 'admin', database='db_name')
        >>> user.name
        u'Administrator'

        :return: the user connected as a browsable record
        :raise: :class:`oerplib.error.RPCError`, :class:`oerplib.error.Error`
        """
        # Raise an error if no database was given
        self._database = database or self._database_default
        if not self._database:
            raise error.Error("No database specified")
        # Get the user's ID and generate the corresponding User record
        try:
            user_id = self.common.login(self._database, user, passwd)
        except rpc.error.ConnectorError as exc:
            raise error.RPCError(exc.message, exc.oerp_traceback)
        else:
            if user_id:
                self._uid = user_id
                self._password = passwd
                self._context = self.execute('res.users', 'context_get')
                self._user = self.browse('res.users', user_id, self._context)
                return self._user
            else:
                #FIXME: Raise an error?
                raise error.RPCError("Wrong login ID or password")

    # ------------------------- #
    # -- Raw XML-RPC methods -- #
    # ------------------------- #

    def execute(self, model, method, *args):
        """Execute the `method` of `model`.
        `*args` parameters varies according to the `method` used.

        >>> oerp.execute('res.partner', 'read', [1, 2], ['name'])
        [{'name': u'ASUStek', 'id': 2}, {'name': u'Your Company', 'id': 1}]

        :return: the result returned by the `method` called
        :raise: :class:`oerplib.error.RPCError`
        """
        self._check_logged_user()
        # Execute the query
        try:
            return self._connector.object.execute(
                self._database, self._uid,
                self._password,
                model, method, *args)
        except rpc.error.ConnectorError as exc:
            raise error.RPCError(exc.message, exc.oerp_traceback)

    def execute_kw(self, model, method, args=None, kwargs=None):
        """Execute the `method` of `model`.
        `args` is a list of parameters (in the right order),
        and `kwargs` a dictionary (named parameters). Both varies according
        to the `method` used.

        >>> oerp.execute_kw('res.partner', 'read', [[1, 2]], {'fields': ['name']})
        [{'name': u'ASUStek', 'id': 2}, {'name': u'Your Company', 'id': 1}]

        .. warning::

            This method only works on servers in version `6.1` and above.

        :return: the result returned by the `method` called
        :raise: :class:`oerplib.error.RPCError`
        """
        self._check_logged_user()
        # Execute the query
        args = args or []
        kwargs = kwargs or {}
        try:
            return self._connector.object.execute_kw(
                self._database, self._uid, self._password,
                model, method, args, kwargs)
        except rpc.error.ConnectorError as exc:
            raise error.RPCError(exc.message, exc.oerp_traceback)

    def exec_workflow(self, model, signal, obj_id):
        """Execute the workflow `signal` on
        the instance having the ID `obj_id` of `model`.

        :raise: :class:`oerplib.error.RPCError`
        """
        #TODO NEED TEST
        self._check_logged_user()
        # Execute the workflow query
        try:
            self._connector.object.exec_workflow(
                self._database, self._uid, self._password,
                model, signal, obj_id)
        except rpc.error.ConnectorError as exc:
            raise error.RPCError(exc.message, exc.oerp_traceback)

    def report(self, report_name, model, obj_ids, report_type='pdf',
               context=None):
        """Download a report from the server and return the local
        path of the file.

        >>> oerp.report('sale.order', 'sale.order', 1)
        '/tmp/oerplib_uJ8Iho.pdf'
        >>> oerp.report('sale.order', 'sale.order', [1, 2])
        '/tmp/oerplib_giZS0v.pdf'

        :return: the path to the generated temporary file
        :raise: :class:`oerplib.error.RPCError`
        """
        #TODO report_type: what it means exactly?

        self._check_logged_user()
        # If no context was supplied, get the default one
        if context is None:
            context = self.context
        # Execute the report query
        try:
            pdf_data = self._get_report_data(report_name, model, obj_ids,
                                             report_type, context)
        except rpc.error.ConnectorError as exc:
            raise error.RPCError(exc.message, exc.oerp_traceback)
        return self._print_file_data(pdf_data)

    def _get_report_data(self, report_name, model, obj_ids,
                         report_type='pdf', context=None):
        """Download binary data of a report from the server."""
        context = context or {}
        obj_ids = [obj_ids] if isinstance(obj_ids, (int, long)) else obj_ids
        data = {
            'model': model,
            'id': obj_ids[0],
            'ids': obj_ids,
            'report_type': report_type,
        }
        try:
            report_id = self._connector.report.report(
                self._database, self.user.id, self._password,
                report_name, obj_ids, data, context)
        except rpc.error.ConnectorError as exc:
            raise error.RPCError(exc.message, exc.oerp_traceback)
        state = False
        attempt = 0
        while not state:
            try:
                pdf_data = self._connector.report.report_get(
                    self._database, self.user.id, self._password,
                    report_id)
            except rpc.error.ConnectorError as exc:
                raise error.RPCError("Unknown error occurred during the "
                                     "download of the report.")
            state = pdf_data['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt > 200:
                raise error.RPCError("Download time exceeded, "
                                     "the operation has been canceled.")
        return pdf_data

    @staticmethod
    def _print_file_data(data):
        """Print data in a temporary file and return the path of this one."""
        if 'result' not in data:
            raise error.InternalError(
                "Invalid data, the operation has been canceled.")
        content = base64.decodestring(data['result'])
        if data.get('code') == 'zlib':
            content = zlib.decompress(content)

        if data['format'] in ['pdf', 'html', 'doc', 'xls',
                              'sxw', 'odt', 'tiff']:
            if data['format'] == 'html' and os.name == 'nt':
                data['format'] = 'doc'
            (file_no, file_path) = tempfile.mkstemp('.' + data['format'],
                                                    'oerplib_')
            with file(file_path, 'wb+') as fp:
                fp.write(content)
            os.close(file_no)
            return file_path

    # ------------------------- #
    # -- High Level methods  -- #
    # ------------------------- #

    def browse(self, model, ids, context=None):
        """Browse one or several records (if `ids` is a list of IDs)
        from `model`. The fields and values for such objects are generated
        dynamically.

        >>> oerp.browse('res.partner', 1)
        browse_record(res.partner, 1)

        >>> [partner.name for partner in oerp.browse('res.partner', [1, 2])]
        [u'Your Company', u'ASUStek']

        A list of data types used by ``browse_record`` fields are
        available :ref:`here <fields>`.

        :return: a ``browse_record`` instance
        :return: a generator to iterate on ``browse_record`` instances
        :raise: :class:`oerplib.error.RPCError`
        """
        return self.get(model).browse(ids, context)

    def search(self, model, args=None, offset=0, limit=None, order=None,
               context=None, count=False):
        """Return a list of IDs of records matching the given criteria in
        `args` parameter. `args` must be of the form
        ``[('name', '=', 'John'), (...)]``

        >>> oerp.search('res.partner', [('name', 'like', 'Agrolait')])
        [3]

        :return: a list of IDs
        :raise: :class:`oerplib.error.RPCError`
        """
        if args is None:
            args = []
        return self.execute(model, 'search', args, offset, limit, order,
                            context, count)

    def create(self, model, vals, context=None):
        """Create a new `model` record with values contained in the `vals`
        dictionary.

        >>> partner_id = oerp.create('res.partner', {'name': 'Jacky Bob', 'lang': 'fr_FR'})

        :return: the ID of the new record.
        :raise: :class:`oerplib.error.RPCError`
        """
        return self.execute(model, 'create', vals, context)

    def read(self, model, ids, fields=None, context=None):
        """Return `fields` values for each `model` record identified by `ids`.
        If `fields` is not specified, all fields values will be retrieved.

        >>> oerp.read('res.partner', [1, 2], ['name'])
        [{'name': u'ASUStek', 'id': 2}, {'name': u'Your Company', 'id': 1}]

        :return: list of dictionaries
        :raise: :class:`oerplib.error.RPCError`
        """
        if fields is None:
            fields = []
        return self.execute(model, 'read', ids, fields, context)

    def write(self, model, ids, vals=None, context=None):
        """Update `model` records identified by `ids` with the given values
        contained in the `vals` dictionary.

        >>> oerp.write('res.users', [1], {'name': "Administrator"})
        True

        :return: `True`
        :raise: :class:`oerplib.error.RPCError`
        """
        #if ids is None:
        #    ids = []
        if vals is None:
            vals = {}
        return self.execute(model, 'write', ids, vals, context)

    def unlink(self, model, ids, context=None):
        """Delete `model` records identified by `ids`.

        >>> oerp.unlink('res.partner', [1])

        :return: `True`
        :raise: :class:`oerplib.error.RPCError`
        """
        #if ids is None:
        #    ids = []
        return self.execute(model, 'unlink', ids, context)

    # ---------------------- #
    # -- Special methods  -- #
    # ---------------------- #

    def write_record(self, browse_record, context=None):
        """.. versionadded:: 0.4

        Update the record corresponding to `browse_record` by sending its values
        to the server (only field values which have been changed).

        >>> partner = oerp.browse('res.partner', 1)
        >>> partner.name = "Test"
        >>> oerp.write_record(partner)  # write('res.partner', [1], {'name': "Test"})

        :return: `True`
        :raise: :class:`oerplib.error.RPCError`
        """
        if not isinstance(browse_record, osv.BrowseRecord):
            raise ValueError("An instance of BrowseRecord is required")
        return osv.Model(self, browse_record.__osv__['name'])._write_record(
            browse_record, context)

    def unlink_record(self, browse_record, context=None):
        """.. versionadded:: 0.4

        Delete the record corresponding to `browse_record` from the server.

        >>> partner = oerp.browse('res.partner', 1)
        >>> oerp.unlink_record(partner)  # unlink('res.partner', [1])

        :return: `True`
        :raise: :class:`oerplib.error.RPCError`
        """
        if not isinstance(browse_record, osv.BrowseRecord):
            raise ValueError("An instance of BrowseRecord is required")
        return osv.Model(self, browse_record.__osv__['name'])._unlink_record(
            browse_record, context)

    def refresh(self, browse_record, context=None):
        """Restore original values on `browse_record` with data
        fetched on the server.
        As a result, all changes made locally on the record are canceled.

        :raise: :class:`oerplib.error.RPCError`
        """
        return osv.Model(self, browse_record.__osv__['name'])._refresh(
            browse_record, context)

    def reset(self, browse_record):
        """Cancel all changes made locally on the `browse_record`.
        No request to the server is executed to perform this operation.
        Therefore, values restored may be outdated.
        """
        return osv.Model(self, browse_record.__osv__['name'])._reset(
            browse_record)

    @staticmethod
    def get_osv_name(browse_record):
        """
        .. deprecated:: 0.7 use the ``__osv__`` attribute instead
           (see :class:`BrowseRecord <oerplib.service.osv.BrowseRecord>`).

        >>> partner = oerp.browse('res.partner', 1)
        >>> oerp.get_osv_name(partner)
        'res.partner'

        :return: the model name of the browsable record

        """
        if not isinstance(browse_record, osv.BrowseRecord):
            raise ValueError("Value is not a browse_record.")
        return browse_record.__osv__['name']

    def get(self, model):
        """.. versionadded:: 0.5

        Return a proxy of the `model` built from the
        server (see :class:`oerplib.service.osv.Model`).

        :return: an instance of :class:`oerplib.service.osv.Model`
        """
        return osv.Model(self, model)

    def save(self, name, rc_file='~/.oerplibrc'):
        """.. versionadded:: 0.8

        Save the session configuration under the name `name`.
        These informations are stored in the ``~/.oerplibrc`` file by default.

            >>> import oerplib
            >>> oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=8069)
            >>> oerp.login('admin', 'admin', 'db_name')
            >>> oerp.save('foo')

        Such informations can be loaded with the :func:`oerplib.load` function
        by returning a pre-configured session of :class:`OERP <oerplib.OERP>`,
        or with the `oerp` command line tool supplied with `oerplib`.
        """
        self._check_logged_user()
        data = {
            'type': self.__class__.__name__,
            'server': self.server,
            'protocol': self.protocol,
            'port': self.port,
            'timeout': self.config['timeout'],
            'user': self.user.login,
            'passwd': self._password,
            'database': self.database,
        }
        session.save(name, data, rc_file)

    @classmethod
    def load(cls, name, rc_file='~/.oerplibrc'):
        """.. versionadded:: 0.8

        Return a :class:`OERP` session pre-configured and connected
        with informations identified by `name`:

            >>> import oerplib
            >>> oerp = oerplib.OERP.load('foo')

        Such informations are stored with the :func:`OERP.save <oerplib.OERP.save>`
        method.
        """
        data = session.get(name, rc_file)
        if data.get('type') != cls.__name__:
            raise error.Error(
                "'{0}' session is not of type '{1}'".format(
                    name, cls.__name__))
        oerp = cls(
            server=data['server'],
            protocol=data['protocol'],
            port=data['port'],
            timeout=data['timeout'],
        )
        oerp.login(
            user=data['user'], passwd=data['passwd'],
            database=data['database'])
        return oerp

    @classmethod
    def list(cls, rc_file='~/.oerplibrc'):
        """.. versionadded:: 0.8

        Return a list of all sessions available in the
        `rc_file` file:

            >>> import oerplib
            >>> oerplib.OERP.list()
            ['foo', 'bar']

        Then, use the :func:`load` function with the desired session:

            >>> oerp = oerplib.OERP.load('foo')
        """
        sessions = session.get_all(rc_file)
        return [name for name, data in sessions.iteritems()
                if data.get('type') == cls.__name__]
        #return session.list(rc_file)

    @classmethod
    def remove(cls, name, rc_file='~/.oerplibrc'):
        """.. versionadded:: 0.8

        Remove the session identified by `name` from the `rc_file` file:

            >>> import oerplib
            >>> oerplib.OERP.remove('foo')
            True
        """
        data = session.get(name, rc_file)
        if data.get('type') != cls.__name__:
            raise error.Error(
                "'{0}' session is not of type '{1}'".format(
                    name, cls.__name__))
        return session.remove(name, rc_file)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
