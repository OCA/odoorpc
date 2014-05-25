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
"""Provide the :class:`DB` class in order to manage the server databases."""

import time

from oerplib import rpc, error


class DB(object):
    """.. versionadded:: 0.4

    The `DB` class represents the database management service.
    It provides functionalities such as list, create, drop, dump
    and restore databases.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.db`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> oerp.db
    <oerplib.service.db.DB object at 0xb75fb04c>

    .. warning::

        All methods documented below are not strictly implemented in `OERPLib`
        (except the
        :func:`create_and_wait <oerplib.service.db.DB.create_and_wait>` method).

        Method calls are purely dynamic, and the following documentation can be
        wrong if the API of the server is changed between versions. Anyway, if
        you know the API proposed by the server for the ``/db`` RPC
        service, it will work.

    .. method:: DB.list()

        Return a list of the databases:

        >>> oerp.db.list()
        ['prod_db', 'test_db']

        :return: a list of database names

    .. method:: DB.list_lang()

        Return a list of codes and names of language supported by the server:

        >>> oerp.db.list_lang()
        [['sq_AL', 'Albanian / Shqipëri'], ['ar_AR', 'Arabic / الْعَرَبيّة'], ...]

        :return: a list of pairs representing languages with their codes and
                 names

    .. method:: DB.server_version()

        Return the version of the server:

        >>> oerp.db.server_version()
        '6.1'

        :return: the version of the server as string

    .. method:: DB.dump(super_admin_passwd, database)

        Return a dump of `database` in `base64`:

        >>> binary_data = oerp.db.dump('super_admin_passwd', 'prod_db')

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: the `base64` string representation of the `database`

    .. method:: DB.restore(super_admin_passwd, database, binary_data)

        Restore in `database` a dump previously created with the
        :func:`dump <DB.dump>` method:

        >>> oerp.db.restore('super_admin_passwd', 'test_db', binary_data)

        The super administrator password `super_admin_passwd` is
        required to perform this action.

    .. method:: DB.drop(super_admin_passwd, database)

        Drop the `database`:

        >>> oerp.db.drop('super_admin_passwd', 'test_db')
        True

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: `True`

    .. method:: DB.create(super_admin_passwd, database, demo_data=False, lang='en_US', admin_passwd='admin')

        Request the server to create a new database named `database`
        which will have `admin_passwd` as administrator password and localized
        with the `lang` parameter.
        You have to set the flag `demo_data` to `True` in order to insert
        demonstration data.

        As the creating process may take some time, you can execute the
        :func:`get_progress <DB.get_progress>` method with the database ID
        returned to know its current state.

        >>> database_id = oerp.db.create('super_admin_passwd', 'test_db', False, 'fr_FR', 'my_admin_passwd')

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: the ID of the new database

    .. method:: DB.get_progress(super_admin_passwd, database_id)

        Check the state of the creating process for the database identified by
        the `database_id` parameter.

        >>> oerp.db.get_progress('super_admin_passwd', database_id) # Just after the call to the 'create' method
        (0, [])
        >>> oerp.db.get_progress('super_admin_passwd', database_id) # Once the database is fully created
        (1.0, [{'login': 'admin', 'password': 'admin', 'name': 'Administrator'},
               {'login': 'demo', 'password': 'demo', 'name': 'Demo User'}])

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: A tuple with the progressing state and a list
                of user accounts created (once the database is fully created).

    .. method:: DB.create_database(super_admin_passwd, database, demo_data=False, lang='en_US', admin_passwd='admin')

        `Available since OpenERP 6.1`

        Similar to :func:`create <DB.create>` but blocking.

        >>> oerp.db.create_database('super_admin_passwd', 'test_db', False, 'fr_FR', 'my_admin_passwd')
        True

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: `True`

    .. method:: DB.duplicate_database(super_admin_passwd, original_database, database)

        `Available since OpenERP 7.0`

        Duplicate `original_database' as `database`.

        >>> oerp.db.duplicate_database('super_admin_passwd', 'prod_db', 'test_db')
        True

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: `True`

    .. method:: DB.rename(super_admin_passwd, old_name, new_name)

        Rename the `old_name` database to `new_name`.

        >>> oerp.db.rename('super_admin_passwd', 'test_db', 'test_db2')
        True

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: `True`

    .. method:: DB.db_exist(database)

        Check if connection to database is possible.

        >>> oerp.db.db_exist('prod_db')
        True

        :return: `True` or `False`

    .. method:: DB.change_admin_password(super_admin_passwd, new_passwd)

        Change the administrator password by `new_passwd`.

        >>> oerp.db.change_admin_password('super_admin_passwd', 'new_passwd')
        True

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: `True`

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def create_and_wait(self, super_admin_passwd, database, demo_data=False,
                        lang='en_US', admin_passwd='admin'):
        """
        .. note::

            This method is not part of the official API. It's just
            a wrapper around the :func:`create <DB.create>` and
            :func:`get_progress <DB.get_progress>` methods. For server
            in version `6.1` or above, please prefer the use of the
            standard :func:`create_database <DB.create_database>` method.

        Like the :func:`create <DB.create>` method, but waits the end of
        the creating process by executing the
        :func:`get_progress <DB.get_progress>` method regularly to check its
        state.

        >>> oerp.db.create_and_wait('super_admin_passwd', 'test_db', False, 'fr_FR', 'my_admin_passwd')
        [{'login': 'admin', 'password': 'my_admin_passwd', 'name': 'Administrateur'},
         {'login': 'demo', 'password': 'demo', 'name': 'Demo User'}]

        The super administrator password `super_admin_passwd` is
        required to perform this action.

        :return: a list of user accounts created
        :raise: :class:`oerplib.error.RPCError`

        """
        try:
            db_id = self._oerp._connector.db.create(
                super_admin_passwd, database, demo_data, lang, admin_passwd)
            progress = 0.0
            attempt = 0
            while progress < 1.0:
                result = self._oerp._connector.db.get_progress(
                    super_admin_passwd, db_id)
                progress = result[0]
                if progress < 1.0:
                    time.sleep(1)
                    attempt += 1
                if attempt > 300:
                    raise error.RPCError(
                        "Too many attempts, the operation"
                        " has been canceled.")
            return result[1]

        except rpc.error.ConnectorError as exc:
            #FIXME handle the exception with the UnicodeEncodeError for
            # the error 'the database already exists'.
            #print dir(exc)
            raise error.RPCError(exc.message, exc.oerp_traceback)

    def __getattr__(self, method):
        """Provide a dynamic access to a RPC method."""
        def rpc_method(*args):
            """Return the result of the RPC request."""
            try:
                meth = getattr(self._oerp._connector.db, method, False)
                return meth(*args)
            except rpc.error.ConnectorError as exc:
                raise error.RPCError(exc.message, exc.oerp_traceback)
        return rpc_method

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
