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
    {u'ir.module.module': [{u'name': u'Technical guide', u'report_type': u'pdf', u'report_name': u'ir.module.reference'}], u'ir.model': [{u'name': u'Model Overview', u'report_type': u'sxw', u'report_name': u'ir.model.overview'}], u'res.partner': [{u'name': u'Labels', u'report_type': u'pdf', u'report_name': u'res.partner'}], u'res.company': [{u'name': u'Preview Report', u'report_type': u'pdf', u'report_name': u'preview.report'}]}

To download a report::

    >>> report = odoo.report.download('preview.report', [1])

The method will return a file-like object, you will have to read its content
in order to save it on your file-system::

    >>> with open('company_preview_report.pdf', 'w') as report_file:
    ...     report_file.write(report.read())
    ...

:ref:`Next step: Save your credentials (session) <tuto-manage-sessions>`
