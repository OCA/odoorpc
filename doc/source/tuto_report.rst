.. _tuto-download-report:

Download reports
****************

Another nice feature is the reports generation with the
:attr:`report <odoorpc.ODOO.report>` property.
The :func:`list <odoorpc.report.Report.list>` method allows you to list
all reports available on your `Odoo` server (classified by models), while the
:func:`download <odoorpc.report.Report.download>` method will
retrieve a report as a file (in PDF, HTML... depending of the report).

To list available reports::

    >>> odoo.report.list()
    {u'account.invoice': [{u'name': u'Duplicates', u'report_type': u'qweb-pdf', u'report_name': u'account.account_invoice_report_duplicate_main'}, {u'name': u'Invoices', u'report_type': u'qweb-pdf', u'report_name': u'account.report_invoice'}], u'res.partner': [{u'name': u'Aged Partner Balance', u'report_type': u'qweb-pdf', u'report_name': u'account.report_agedpartnerbalance'}, {u'name': u'Due Payments', u'report_type': u'qweb-pdf', u'report_name': u'account.report_overdue'}], ...}

To download a report::

    >>> report = odoo.report.download('account.report_invoice', [1])

The method will return a file-like object, you will have to read its content
in order to save it on your file-system::

    >>> with open('invoice.pdf', 'w') as report_file:
    ...     report_file.write(report.read())
    ...

:ref:`Next step: Save your credentials (session) <tuto-manage-sessions>`
