# -*- coding: utf-8 -*-
# Copyright 2014 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""This module provide the :class:`Report` class to list available reports and
to generate/download them.
"""
import base64
import io

from odoorpc.tools import get_encodings, v


def encode2bytes(data):
    for encoding in get_encodings():
        try:
            return data.decode(encoding)
        except Exception:
            pass
    return data


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

        Warning: this feature is not supported for Odoo >= 14 (CSRF token required).

        For instance, to download the "Quotation / Order" report of sale orders
        identified by the IDs ``[2, 3]``:

        .. doctest::
            :options: +SKIP

            >>> report = odoo.report.download('sale.report_saleorder', [2, 3])

        .. doctest::
            :hide:

            >>> from odoorpc.tools import v
            >>> if v(VERSION) < v('14.0'):
            ...     report = odoo.report.download('sale.report_saleorder', [2])

        Write it on the file system:

        .. doctest::
            :options: +SKIP

            >>> with open('sale_orders.pdf', 'wb') as report_file:
            ...     report_file.write(report.read())
            ...

        .. doctest::
            :hide:

            >>> from odoorpc.tools import v
            >>> if v(VERSION) < v('14.0'):
            ...     with open('sale_orders.pdf', 'wb') as report_file:
            ...         fileno = report_file.write(report.read())   # Python 3
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

        def check_report(name):
            report_model = 'ir.actions.report'
            if v(self._odoo.version)[0] < 11:
                report_model = 'ir.actions.report.xml'
            IrReport = self._odoo.env[report_model]
            report_ids = IrReport.search([('report_name', '=', name)])
            report_id = report_ids and report_ids[0] or False
            if not report_id:
                raise ValueError("The report '%s' does not exist." % name)
            return report_id

        report_id = check_report(name)

        # Odoo >= 11.0
        if v(self._odoo.version)[0] >= 11:
            IrReport = self._odoo.env['ir.actions.report']
            report = IrReport.browse(report_id)
            if v(self._odoo.version)[0] >= 14:
                # Need a CSRF token to print reports on Odoo >= 14
                raise NotImplementedError
                # response = report.with_context(context)._render(
                #     ids, data=datas
                # )
            else:
                response = report.with_context(context).render(ids, data=datas)
            content = response[0]
            # On the server the result is a bytes string,
            # but the RPC layer of Odoo returns it as a unicode string,
            # so we encode it again as bytes
            result = content.encode('latin1')
            return io.BytesIO(result)
        # Odoo < 11.0
        else:
            args_to_send = [
                self._odoo.env.db,
                self._odoo.env.uid,
                self._odoo._password,
                name,
                ids,
                datas,
                context,
            ]
            data = self._odoo.json(
                '/jsonrpc',
                {
                    'service': 'report',
                    'method': 'render_report',
                    'args': args_to_send,
                },
            )
            if 'result' not in data and not data['result'].get('result'):
                raise ValueError("Received invalid data.")
            # Encode to bytes forced to be compatible with Python 3.2
            # (its 'base64.standard_b64decode()' function only accepts bytes)
            result = encode2bytes(data['result']['result'])
            content = base64.standard_b64decode(result)
            return io.BytesIO(content)

    def list(self):
        """List available reports from the server.

        It returns a dictionary with reports classified by data model:

        .. doctest::
            :options: +SKIP

            >>> from odoorpc.tools import v
            >>> inv_model = 'account.move'
            >>> if v(VERSION) < v('13.0'):
            ...     inv_model = 'account.invoice'
            >>> odoo.report.list()[inv_model]
            [{'name': u'Duplicates',
              'report_name': u'account.account_invoice_report_duplicate_main',
              'report_type': u'qweb-pdf'},
             {'name': 'Invoices',
              'report_type': 'qweb-pdf',
              'report_name': 'account.report_invoice'}]

        .. doctest::
            :hide:

            >>> from odoorpc.tools import v
            >>> inv_model = 'account.move'
            >>> if v(VERSION) < v('13.0'):
            ...     inv_model = 'account.invoice'
            >>> from pprint import pprint as pp
            >>> any(data['report_name'] == 'account.report_invoice'
            ...     for data in odoo.report.list()[inv_model])
            True

        *Python 2:*

        :return: `list` of dictionaries
        :raise: `urllib2.URLError` (connection error)

        *Python 3:*

        :return: `list` of dictionaries
        :raise: `urllib.error.URLError` (connection error)
        """
        report_model = 'ir.actions.report'
        if v(self._odoo.version)[0] < 11:
            report_model = 'ir.actions.report.xml'
        IrReport = self._odoo.env[report_model]
        report_ids = IrReport.search([])
        reports = IrReport.read(
            report_ids, ['name', 'model', 'report_name', 'report_type']
        )
        result = {}
        for report in reports:
            model = report.pop('model')
            report.pop('id')
            if model not in result:
                result[model] = []
            result[model].append(report)
        return result
