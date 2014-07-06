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
"""This module contains the ``ODOO`` class which is the entry point to manage
an `Odoo` server.
"""
from odoorpc import rpc, error, tools
from odoorpc.tools import session
from odoorpc.service import osv
from odoorpc.service.db import DB


class ODOO(object):
    """Return a new instance of the :class:`ODOO` class.
    `JSON-RPC` protocol is used to make requests, and the respective values
    for the `protocol` parameter are ``jsonrpc`` (default) and ``jsonrpc+ssl``.

        >>> import odoorpc
        >>> odoo = odoorpc.ODOO('localhost', protocol='jsonrpc', port=8069)

    `OdooRPC` will try by default to detect the server version in order to
    adapt its requests if necessary. However, it is possible to force the
    version to use with the `version` parameter:

        >>> odoo = odoorpc.ODOO('localhost', version='8.0')

    :raise: :class:`odoorpc.error.InternalError`
    :raise: `ValueError`
    """

    def __init__(self, host='localhost', protocol='jsonrpc',
                 port=8069, timeout=120, version=None):
        if protocol not in ['jsonrpc', 'jsonrpc+ssl']:
            txt = ("The protocol '{0}' is not supported by the ODOO class. "
                   "Please choose a protocol among these ones: {1}")
            txt = txt.format(protocol, ['jsonrpc', 'jsonrpc+ssl'])
            raise ValueError(txt)
        try:
            port = int(port)
        except ValueError:
            raise ValueError("The port must be an integer")
        try:
            timeout = int(timeout)
        except ValueError:
            raise ValueError("The timeout must be an integer")
        self._host = host
        self._port = port
        self._protocol = protocol
        self._database = None
        self._uid = None
        self._password = None
        self._user = None
        self._context = None
        self._db = DB(self)
        # Instanciate the server connector
        try:
            self._connector = rpc.PROTOCOLS[protocol](
                self._host, self._port, timeout, version)
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

        >>> odoo.config
        {'auto_context': True, 'timeout': 120}

        - ``auto_context``: if set to `True`, the user context will be sent
          automatically to every call of a
          :class:`model <odoorpc.service.osv.Model>` method (default: `True`):

            >>> product_osv = odoo.get('product.product')
            >>> product_osv.name_get([3]) # Context sent by default ('lang': 'fr_FR' here)
            [[3, '[PC1] PC Basic']]
            >>> odoo.config['auto_context'] = False
            >>> product_osv.name_get([3]) # No context sent
            [[3, '[PC1] Basic PC']]

        - ``timeout``: set the maximum timeout in seconds for a RPC request
          (default: `120`):

            >>> odoo.config['timeout'] = 300

        """
        return self._config

    # Readonly properties
    @property
    def user(self):
        """The browsable record of the user connected.

        >>> odoo.login('db_name', 'admin', 'admin') == odoo.user
        True

        """
        return self._user

    @property
    def context(self):
        """The context of the user connected.

        >>> odoo.login('db_name', 'admin', 'admin')
        browse_record('res.users', 1)
        >>> odoo.context
        {'lang': 'fr_FR', 'tz': False}
        >>> odoo.context['lang'] = 'en_US'

        """
        return self._context

    @property
    def version(self):
        """The version of the server.

        >>> odoo.version
        '8.0'
        """
        return self._connector.version

    @property
    def db(self):
        """The database management service.
        See the :class:`odoorpc.service.db.DB` class.
        """
        return self._db

    host = property(lambda self: self._host,
                    doc="Hostname of IP address of the the server.")
    port = property(lambda self: self._port,
                    doc="The port used.")
    protocol = property(lambda self: self._protocol,
                        doc="The protocol used.")
    database = property(lambda self: self._database, doc="The database currently used.")

    def json(self, url, params):
        """Low level method to execute JSON queries.
        It basically performs a request and raises an
        :class:`odoorpc.error.RPCError` exception if the response contains
        an error.

        You have to know the names of each parameter required by the function
        called, and set them in the `params` dictionary.

        Here an authentication request:

        >>> data = odoo.json(
        ...     '/web/session/authenticate',
        ...     {'db': 'db_name', 'login':'admin', 'password': 'admin'})
        >>> from pprint import pprint as pp
        >>> pp(data)
        {u'id': 645674382,
         u'jsonrpc': u'2.0',
         u'result': {u'db': u'db_name',
                     u'session_id': u'fa740abcb91784b8f4750c5c5b14da3fcc782d11',
                     u'uid': 1,
                     u'user_context': {u'lang': u'en_US',
                                       u'tz': u'Europe/Brussels',
                                       u'uid': 1},
                     u'username': u'admin'}}

        And a call to the ``read`` method of the ``res.users`` model:

        >>> data = odoo.json(
        ...     '/web/dataset/call',
        ...     {'model': 'res.users', 'method': 'read',
        ...      'args': [[1], ['name']]})
        >>> pp(data)
        {u'id': 756578441,
         u'jsonrpc': u'2.0',
         u'result': [{u'id': 1, u'name': u'Administrator'}]}

        :return: a dictionary (JSON response)
        :raise: :class:`odoorpc.error.RPCError`
        :raise: `urllib2.HTTPError`

        """
        data = self._connector.proxy_json(url, params)
        if data.get('error'):
            message = ', '.join(
                "%s" % arg for arg in data['error']['data']['arguments'])
            traceback = data['error']['data']['debug']
            raise error.RPCError(message, traceback)
        return data

    def http(self, url, data, headers=None):
        """Low level method to execute raw HTPP queries.

        .. note::

            For low level JSON-RPC queries, see the more convenient
            :func:`odoorpc.ODOO.json` method instead.

        You have to know the names of each POST parameter required by the
        URL, and set them in the `data` string/buffer.
        The `data` argument must be built by yourself, following the expected
        URL parameters (with :func:`urllib.urlencode` function for simple
        parameters, or multipart/form-data structure to handle file upload).

        E.g., the HTTP raw query to backup a database on `Odoo 8.0`:

        >>> response = odoo.http(
        ...     'web/database/backup',
        ...     'token=foo&backup_pwd=admin&backup_db=db_name')
        >>> response
        <addinfourl at 139685107812904 whose fp = <socket._fileobject object at 0x7f0afbd535d0>>
        >>> binary_data = response.read()

        :return: `urllib.addinfourl`
        :raise: `urllib2.HTTPError`

        """
        return self._connector.proxy_http(url, data, headers)

    # NOTE: in the past this function was implemented as a decorator for
    # methods needing to be checked, but Sphinx documentation generator is not
    # able to parse decorated methods.
    def _check_logged_user(self):
        """Check if a user is logged. Otherwise, an error is raised."""
        if not self._uid or not self._password:
            raise error.LoginError(u"User login required.")

    def login(self, db, login='admin', password='admin'):
        """Log in as the given `user` with the password `passwd` on the
        database `db` and return the corresponding user as a browsable
        record (from the ``res.users`` model).

        >>> user = odoo.login('db_name', 'admin', 'admin')
        >>> user.name
        u'Administrator'

        :return: the user connected as a browsable record
        :raise: :class:`odoorpc.error.RPCError`, :class:`odoorpc.error.LoginError`
        :raise: `urllib2.HTTPError`
        """
        # Get the user's ID and generate the corresponding user record
        data = self.json(
            '/web/session/authenticate',
            {'db': db, 'login': login, 'password': password})
        user_id = data['result']['uid']
        if user_id:
            self._database = db
            self._uid = user_id
            self._password = password
            self._context = data['result']['user_context']
            user_obj = self.get('res.users')
            self._user = user_obj.browse(user_id, context=self._context)
            return self._user
        else:
            raise error.LoginError("Wrong login ID or password")

    def logout(self):
        """Log out the user.

        >>> odoo.logout()
        True

        :return: `True` if the operation succeed, `False` if no user was logged
        :raise: :class:`odoorpc.error.RPCError`
        :raise: `urllib2.HTTPError`
        """
        if not self._uid:
            return False
        self.json('/web/session/destroy', {})
        self._database = self._uid = self._password = self._context = None
        self._user = None
        return True

    # ------------------------- #
    # -- Raw XML-RPC methods -- #
    # ------------------------- #

    def execute(self, model, method, *args):
        """Execute the `method` of `model`.
        `*args` parameters varies according to the `method` used.

        >>> odoo.execute('res.partner', 'read', [1, 2], ['name'])
        [{'name': u'ASUStek', 'id': 2}, {'name': u'Your Company', 'id': 1}]

        :return: the result returned by the `method` called
        :raise: :class:`odoorpc.error.RPCError`
        :raise: `urllib2.HTTPError`
        """
        self._check_logged_user()
        # Execute the query
        data = self.json(
            '/web/dataset/call',
            {'model': model, 'method': method, 'args': args})
        return data['result']

    def execute_kw(self, model, method, args=None, kwargs=None):
        """Execute the `method` of `model`.
        `args` is a list of parameters (in the right order),
        and `kwargs` a dictionary (named parameters). Both varies according
        to the `method` used.

        >>> odoo.execute_kw('res.partner', 'read', [[1, 2]], {'fields': ['name']})
        [{'name': u'ASUStek', 'id': 2}, {'name': u'Your Company', 'id': 1}]

        :return: the result returned by the `method` called
        :raise: :class:`odoorpc.error.RPCError`
        :raise: `urllib2.HTTPError`
        """
        self._check_logged_user()
        # Execute the query
        args = args or []
        kwargs = kwargs or {}
        data = self.json(
            '/web/dataset/call_kw',
            {'model': model, 'method': method,
                'args': args, 'kwargs': kwargs})
        return data['result']

    def exec_workflow(self, model, obj_id, signal):
        """Execute the workflow `signal` on
        the instance having the ID `obj_id` of `model`.

        :raise: :class:`odoorpc.error.RPCError`
        :raise: `urllib2.HTTPError`
        """
        self._check_logged_user()
        # Execute the workflow query
        data = self.json(
            '/web/dataset/exec_workflow',
            {'model': model, 'id': obj_id, 'signal': signal})
        return data['result']

    #def report(self, report_name, model, obj_ids, report_type='pdf',
    #           context=None):
    #    """Download a report from the server and return the local
    #    path of the file.

    #    >>> odoo.report('sale.order', 'sale.order', 1)
    #    '/tmp/odoorpc_uJ8Iho.pdf'
    #    >>> odoo.report('sale.order', 'sale.order', [1, 2])
    #    '/tmp/odoorpc_giZS0v.pdf'

    #    :return: the path to the generated temporary file
    #    :raise: :class:`odoorpc.error.RPCError`
    #    """
    #    #TODO report_type: what it means exactly?

    #    self._check_logged_user()
    #    # If no context was supplied, get the default one
    #    if context is None:
    #        context = self.context
    #    # Execute the report query
    #    try:
    #        pdf_data = self._get_report_data(report_name, model, obj_ids,
    #                                         report_type, context)
    #    except rpc.error.ConnectorError as exc:
    #        raise error.RPCError(exc.message, exc.odoo_traceback)
    #    return self._print_file_data(pdf_data)

    #def _get_report_data(self, report_name, model, obj_ids,
    #                     report_type='pdf', context=None):
    #    """Download binary data of a report from the server."""
    #    context = context or {}
    #    obj_ids = [obj_ids] if isinstance(obj_ids, (int, long)) else obj_ids
    #    data = {
    #        'model': model,
    #        'id': obj_ids[0],
    #        'ids': obj_ids,
    #        'report_type': report_type,
    #    }
    #    try:
    #        report_id = self._connector.report.report(
    #            self._database, self.user.id, self._password,
    #            report_name, obj_ids, data, context)
    #    except rpc.error.ConnectorError as exc:
    #        raise error.RPCError(exc.message, exc.odoo_traceback)
    #    state = False
    #    attempt = 0
    #    while not state:
    #        try:
    #            pdf_data = self._connector.report.report_get(
    #                self._database, self.user.id, self._password,
    #                report_id)
    #        except rpc.error.ConnectorError as exc:
    #            raise error.RPCError("Unknown error occurred during the "
    #                                 "download of the report.")
    #        state = pdf_data['state']
    #        if not state:
    #            time.sleep(1)
    #            attempt += 1
    #        if attempt > 200:
    #            raise error.RPCError("Download time exceeded, "
    #                                 "the operation has been canceled.")
    #    return pdf_data

    #@staticmethod
    #def _print_file_data(data):
    #    """Print data in a temporary file and return the path of this one."""
    #    if 'result' not in data:
    #        raise error.InternalError(
    #            "Invalid data, the operation has been canceled.")
    #    content = base64.decodestring(data['result'])
    #    if data.get('code') == 'zlib':
    #        content = zlib.decompress(content)

    #    if data['format'] in ['pdf', 'html', 'doc', 'xls',
    #                          'sxw', 'odt', 'tiff']:
    #        if data['format'] == 'html' and os.name == 'nt':
    #            data['format'] = 'doc'
    #        (file_no, file_path) = tempfile.mkstemp('.' + data['format'],
    #                                                'odoorpc_')
    #        with file(file_path, 'wb+') as fp:
    #            fp.write(content)
    #        os.close(file_no)
    #        return file_path

    # ---------------------- #
    # -- Special methods  -- #
    # ---------------------- #

    def write_record(self, browse_record, context=None):
        """Update the record corresponding to `browse_record` by sending its values
        to the server (only field values which have been changed).

        >>> partner = odoo.browse('res.partner', 1)
        >>> partner.name = "Test"
        >>> odoo.write_record(partner)  # write('res.partner', [1], {'name': "Test"})

        :return: `True`
        :raise: :class:`odoorpc.error.RPCError`
        """
        if not isinstance(browse_record, osv.BrowseRecord):
            raise ValueError("An instance of BrowseRecord is required")
        return osv.Model(self, browse_record.__osv__['name'])._write_record(
            browse_record, context)

    def unlink_record(self, browse_record, context=None):
        """Delete the record corresponding to `browse_record` from the server.

        >>> partner = odoo.browse('res.partner', 1)
        >>> odoo.unlink_record(partner)  # unlink('res.partner', [1])

        :return: `True`
        :raise: :class:`odoorpc.error.RPCError`
        """
        if not isinstance(browse_record, osv.BrowseRecord):
            raise ValueError("An instance of BrowseRecord is required")
        return osv.Model(self, browse_record.__osv__['name'])._unlink_record(
            browse_record, context)

    def refresh(self, browse_record, context=None):
        """Restore original values on `browse_record` with data
        fetched on the server.
        As a result, all changes made locally on the record are canceled.

        :raise: :class:`odoorpc.error.RPCError`
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

    def get(self, model):
        """Return a proxy of the `model` built from the
        server (see :class:`odoorpc.service.osv.Model`).

        :return: an instance of :class:`odoorpc.service.osv.Model`
        """
        return osv.Model(self, model)

    def save(self, name, rc_file='~/.odoorpcrc'):
        """Save the session configuration under the name `name`.
        These informations are stored in the ``~/.odoorpcrc`` file by default.

            >>> import odoorpc
            >>> odoo = odoorpc.ODOO('localhost', port=8069)
            >>> odoo.login('db_name', 'admin', 'admin')
            >>> odoo.save('foo')

        Such informations can be loaded with the :func:`odoorpc.load` function
        by returning a pre-configured session of :class:`ODOO <odoorpc.ODOO>`,
        or with the `odoo` command line tool supplied with `odoorpc`.
        """
        self._check_logged_user()
        data = {
            'type': self.__class__.__name__,
            'host': self.host,
            'protocol': self.protocol,
            'port': self.port,
            'timeout': self.config['timeout'],
            'user': self.user.login,
            'passwd': self._password,
            'database': self.db,
        }
        session.save(name, data, rc_file)

    @classmethod
    def load(cls, name, rc_file='~/.odoorpcrc'):
        """Return a :class:`ODOO` session pre-configured and connected
        with informations identified by `name`:

            >>> import odoorpc
            >>> odoo = odoorpc.ODOO.load('foo')

        Such informations are stored with the :func:`ODOO.save <odoorpc.ODOO.save>`
        method.
        """
        data = session.get(name, rc_file)
        if data.get('type') != cls.__name__:
            raise error.Error(
                "'{0}' session is not of type '{1}'".format(
                    name, cls.__name__))
        odoo = cls(
            host=data['host'],
            protocol=data['protocol'],
            port=data['port'],
            timeout=data['timeout'],
        )
        odoo.login(
            db=data['database'], login=data['user'], password=data['passwd'])
        return odoo

    @classmethod
    def list(cls, rc_file='~/.odoorpcrc'):
        """Return a list of all sessions available in the
        `rc_file` file:

            >>> import odoorpc
            >>> odoorpc.ODOO.list()
            ['foo', 'bar']

        Then, use the :func:`load` function with the desired session:

            >>> odoo = odoorpc.ODOO.load('foo')
        """
        sessions = session.get_all(rc_file)
        return [name for name, data in sessions.iteritems()
                if data.get('type') == cls.__name__]
        #return session.list(rc_file)

    @classmethod
    def remove(cls, name, rc_file='~/.odoorpcrc'):
        """Remove the session identified by `name` from the `rc_file` file:

            >>> import odoorpc
            >>> odoorpc.ODOO.remove('foo')
            True
        """
        data = session.get(name, rc_file)
        if data.get('type') != cls.__name__:
            raise error.Error(
                "'{0}' session is not of type '{1}'".format(
                    name, cls.__name__))
        return session.remove(name, rc_file)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
