# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""Provide the :class:`DB` class to manage the server databases."""
import base64
import io
import sys

from odoorpc import error
from odoorpc.tools import v

# Python 2
if sys.version_info[0] < 3:

    def encode2bytes(data):
        return data


# Python >= 3
else:

    def encode2bytes(data):
        return bytes(data, 'ascii')


class DB(object):
    """The `DB` class represents the database management service.
    It provides functionalities such as list, create, drop, dump
    and restore databases.

    .. note::
        This service have to be used through the :attr:`odoorpc.ODOO.db`
        property.

    >>> import odoorpc
    >>> odoo = odoorpc.ODOO('localhost')    # doctest: +SKIP
    >>> odoo.db
    <odoorpc.db.DB object at 0x...>

    """

    def __init__(self, odoo):
        self._odoo = odoo

    def dump(self, password, db, format_='zip'):
        """Backup the `db` database. Returns the dump as a binary ZIP file
        containing the SQL dump file alongside the filestore directory (if any).

        >>> dump = odoo.db.dump('super_admin_passwd', 'prod') # doctest: +SKIP

        .. doctest::
            :hide:

            >>> dump = odoo.db.dump(SUPER_PWD, DB)

        If you get a timeout error, increase this one before performing the
        request:

        >>> timeout_backup = odoo.config['timeout']
        >>> odoo.config['timeout'] = 600    # Timeout set to 10 minutes
        >>> dump = odoo.db.dump('super_admin_passwd', 'prod')   # doctest: +SKIP
        >>> odoo.config['timeout'] = timeout_backup

        Write it on the file system:

        .. doctest::
            :options: +SKIP

            >>> with open('dump.zip', 'wb') as dump_zip:
            ...     dump_zip.write(dump.read())
            ...

        .. doctest::
            :hide:

            >>> with open('dump.zip', 'wb') as dump_zip:
            ...     fileno = dump_zip.write(dump.read())    # Python 3
            ...

        You can manipulate the file with the `zipfile` module for instance:

        .. doctest::
            :options: +SKIP

            >>> import zipfile
            >>> zipfile.ZipFile('dump.zip').namelist()
            ['dump.sql',
            'filestore/ef/ef2c882a36dbe90fc1e7e28d816ad1ac1464cfbb',
            'filestore/dc/dcf00aacce882bbfd117c0277e514f829b4c5bf0',
             ...]

        .. doctest::
            :hide:

            >>> import zipfile
            >>> zipfile.ZipFile('dump.zip').namelist() # doctest: +NORMALIZE_WHITESPACE
            ['dump.sql'...'filestore/...'...]

        The super administrator password is required to perform this method.

        *Python 2:*

        :return: `io.BytesIO`
        :raise: :class:`odoorpc.error.RPCError` (access denied / wrong database)
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :return: `io.BytesIO`
        :raise: :class:`odoorpc.error.RPCError` (access denied / wrong database)
        :raise: `urllib.error.URLError` (connection error)
        """
        args = [password, db]
        if v(self._odoo.version)[0] >= 9:
            args.append(format_)
        data = self._odoo.json(
            '/jsonrpc', {'service': 'db', 'method': 'dump', 'args': args}
        )
        # Encode to bytes forced to be compatible with Python 3.2
        # (its 'base64.standard_b64decode()' function only accepts bytes)
        result = encode2bytes(data['result'])
        content = base64.standard_b64decode(result)
        return io.BytesIO(content)

    def change_password(self, password, new_password):
        """Change the administrator password by `new_password`.

        >>> odoo.db.change_password('super_admin_passwd', 'new_admin_passwd') # doctest: +SKIP

        .. doctest:
            :hide:

            >>> odoo.db.change_password(SUPER_PWD, 'new_admin_passwd')
            >>> odoo.db.change_password('new_admin_passwd', SUPER_PWD)

        The super administrator password is required to perform this method.

        *Python 2:*

        :raise: :class:`odoorpc.error.RPCError` (access denied)
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :raise: :class:`odoorpc.error.RPCError` (access denied)
        :raise: `urllib.error.URLError` (connection error)
        """
        self._odoo.json(
            '/jsonrpc',
            {
                'service': 'db',
                'method': 'change_admin_password',
                'args': [password, new_password],
            },
        )

    def create(
        self, password, db, demo=False, lang='en_US', admin_password='admin'
    ):
        """Request the server to create a new database named `db`
        which will have `admin_password` as administrator password and
        localized with the `lang` parameter.
        You have to set the flag `demo` to `True` in order to insert
        demonstration data.

        >>> odoo.db.create('super_admin_passwd', 'prod', False, 'fr_FR', 'my_admin_passwd') # doctest: +SKIP

        If you get a timeout error, increase this one before performing the
        request:

        >>> timeout_backup = odoo.config['timeout']
        >>> odoo.config['timeout'] = 600    # Timeout set to 10 minutes
        >>> odoo.db.create('super_admin_passwd', 'prod', False, 'fr_FR', 'my_admin_passwd') # doctest: +SKIP
        >>> odoo.config['timeout'] = timeout_backup

        The super administrator password is required to perform this method.

        *Python 2:*

        :raise: :class:`odoorpc.error.RPCError` (access denied)
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :raise: :class:`odoorpc.error.RPCError` (access denied)
        :raise: `urllib.error.URLError` (connection error)
        """
        self._odoo.json(
            '/jsonrpc',
            {
                'service': 'db',
                'method': 'create_database',
                'args': [password, db, demo, lang, admin_password],
            },
        )

    def drop(self, password, db):
        """Drop the `db` database. Returns `True` if the database was removed,
        `False` otherwise (database did not exist):

        >>> odoo.db.drop('super_admin_passwd', 'test') # doctest: +SKIP
        True

        The super administrator password is required to perform this method.

        *Python 2:*

        :return: `True` or `False`
        :raise: :class:`odoorpc.error.RPCError` (access denied)
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :return: `True` or `False`
        :raise: :class:`odoorpc.error.RPCError` (access denied)
        :raise: `urllib.error.URLError` (connection error)
        """
        if self._odoo._env and self._odoo._env.db == db:
            # Remove the existing session to avoid HTTP session error
            self._odoo.logout()
        data = self._odoo.json(
            '/jsonrpc',
            {'service': 'db', 'method': 'drop', 'args': [password, db]},
        )
        return data['result']

    def duplicate(self, password, db, new_db):
        """Duplicate `db' as `new_db`.

        >>> odoo.db.duplicate('super_admin_passwd', 'prod', 'test') # doctest: +SKIP

        The super administrator password is required to perform this method.

        *Python 2:*

        :raise: :class:`odoorpc.error.RPCError` (access denied / wrong database)
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :raise: :class:`odoorpc.error.RPCError` (access denied / wrong database)
        :raise: `urllib.error.URLError` (connection error)
        """
        self._odoo.json(
            '/jsonrpc',
            {
                'service': 'db',
                'method': 'duplicate_database',
                'args': [password, db, new_db],
            },
        )

    def list(self):
        """Return the list of the databases:

        >>> odoo.db.list() # doctest: +SKIP
        ['prod', 'test']

        *Python 2:*

        :return: `list` of database names
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :return: `list` of database names
        :raise: `urllib.error.URLError` (connection error)
        """
        data = self._odoo.json(
            '/jsonrpc', {'service': 'db', 'method': 'list', 'args': []}
        )
        return data.get('result', [])

    def restore(self, password, db, dump, copy=False):
        """Restore the `dump` database into the new `db` database.
        The `dump` file object can be obtained with the
        :func:`dump <DB.dump>` method.
        If `copy` is set to `True`, the restored database will have a new UUID.

        >>> odoo.db.restore('super_admin_passwd', 'test', dump_file) # doctest: +SKIP

        If you get a timeout error, increase this one before performing the
        request:

        >>> timeout_backup = odoo.config['timeout']
        >>> odoo.config['timeout'] = 7200   # Timeout set to 2 hours
        >>> odoo.db.restore('super_admin_passwd', 'test', dump_file) # doctest: +SKIP
        >>> odoo.config['timeout'] = timeout_backup

        The super administrator password is required to perform this method.

        *Python 2:*

        :raise: :class:`odoorpc.error.RPCError`
                (access denied / database already exists)
        :raise: :class:`odoorpc.error.InternalError` (dump file closed)
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :raise: :class:`odoorpc.error.RPCError`
                (access denied / database already exists)
        :raise: :class:`odoorpc.error.InternalError` (dump file closed)
        :raise: `urllib.error.URLError` (connection error)
        """
        if dump.closed:
            raise error.InternalError("Dump file closed")
        b64_data = base64.standard_b64encode(dump.read()).decode()
        self._odoo.json(
            '/jsonrpc',
            {
                'service': 'db',
                'method': 'restore',
                'args': [password, db, b64_data, copy],
            },
        )
