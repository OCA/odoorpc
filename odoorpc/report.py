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
"""This module provide the :class:`Report` class to list available reports and
to generate/download them.
"""
import base64
import io
import sys
# Python 2
if sys.version_info[0] < 3:
    def encode2bytes(data):
        return data
# Python >= 3
else:
    def encode2bytes(data):
        return bytes(data, 'ascii')


class Report(object):
    """The `Report` class represents the report management service.
    It provides methods to list and download available reports from the server.

    .. note::
        This service have to be used through the :attr:`odoorpc.ODOO.report`
        property.

    .. doctest::
        :options: +SKIP

        >>> import odoorpc
        >>> odoo = odoorpc.ODOO('localhost', port=8069)
        >>> odoo.login('odoorpc_test', 'admin', 'password')
        >>> odoo.report
        <odoorpc.report.Report object at 0x7f82fe7a1d50>

    .. doctest::
        :hide:

        >>> import odoorpc
        >>> odoo = odoorpc.ODOO(HOST, protocol=PROTOCOL, port=PORT)
        >>> odoo.login(DB, USER, PWD)
        >>> odoo.report
        <odoorpc.report.Report object at ...>
    """
    def __init__(self, odoo):
        self._odoo = odoo

    def download(self, name, ids, datas=None, context=None):
        """Download a report from the server and return it as a remote file.
        For instance, to download the "Quotation / Order" report of sale orders
        identified by the IDs ``[2, 3]``:

        .. doctest::

            >>> report = odoo.report.download('sale.report_saleorder', [2, 3])

        Write it on the file system:

        .. doctest::
            :options: +SKIP

            >>> with open('sale_orders.pdf', 'wb') as report_file:
            ...     report_file.write(report.read())
            ...

        .. doctest::
            :hide:

            >>> with open('sale_orders.pdf', 'wb') as report_file:
            ...     fileno = report_file.write(report.read())   # Python 3
            ...

        *Python 2:*

        :return: `io.BytesIO`
        :raise: :class:`odoorpc.error.RPCError` (wrong parameters)
        :raise: `ValueError`  (received invalid data)
        :raise: `urllib2.URLError`  (connection error)

        *Python 3:*

        :return: `io.BytesIO`
        :raise: :class:`odoorpc.error.RPCError` (wrong parameters)
        :raise: `ValueError`  (received invalid data)
        :raise: `urllib.error.URLError` (connection error)
        """
        if context is None:
            context = self._odoo.env.context
        args_to_send = [self._odoo.env.db,
                        self._odoo.env.uid, self._odoo._password,
                        name, ids, datas, context]
        data = self._odoo.json(
            '/jsonrpc',
            {'service': 'report',
             'method': 'render_report',
             'args': args_to_send})
        if 'result' not in data and not data['result'].get('result'):
            raise ValueError("Received invalid data.")
        # Encode to bytes forced to be compatible with Python 3.2
        # (its 'base64.standard_b64decode()' function only accepts bytes)
        result = encode2bytes(data['result']['result'])
        content = base64.standard_b64decode(result)
        return io.BytesIO(content)

    def list(self):
        """List available reports from the server by returning a dictionary
        with reports classified by data model:

        .. doctest::
            :options: +SKIP

            >>> odoo.report.list()['account.invoice']
            [{'name': u'Duplicates',
              'report_name': u'account.account_invoice_report_duplicate_main',
              'report_type': u'qweb-pdf'},
             {'name': 'Invoices',
              'report_type': 'qweb-pdf',
              'report_name': 'account.report_invoice'}]

        .. doctest::
            :hide:

            >>> from pprint import pprint as pp
            >>> any(data['report_name'] == 'account.report_invoice'
            ...     for data in odoo.report.list()['account.invoice'])
            True

        *Python 2:*

        :return: `list` of dictionaries
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :return: `list` of dictionaries
        :raise: `urllib.error.URLError` (connection error)
        """
        Report = self._odoo.env['ir.actions.report.xml']
        report_ids = Report.search([])
        reports = Report.read(
            report_ids, ['name', 'model', 'report_name', 'report_type'])
        result = {}
        for report in reports:
            model = report.pop('model')
            report.pop('id')
            if model not in result:
                result[model] = []
            result[model].append(report)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
