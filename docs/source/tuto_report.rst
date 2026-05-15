.. _tuto-download-report:

Download reports
****************

Another nice feature is the reports generation with the
:attr:`report <odoorpc.ODOO.report>` property.
The :func:`list <odoorpc.report.Report.list>` method allows you to list
all reports available on your `Odoo` server (classified by models), while the
:func:`download <odoorpc.report.Report.download>` method will
retrieve a report as a file (in PDF, HTML... depending of the report).

To list available reports grouped by models::

    >>> from pprint import pprint
    >>> pprint(odoo.report.list())
    {'account.common.journal.report': [{'name': 'Journals Audit',
                                        'report_name': 'account.report_journal',
                                        'report_type': 'qweb-pdf'}],
     'account.invoice': [{'name': 'Invoices',
                          'report_name': 'account.report_invoice_with_payments',
                          'report_type': 'qweb-pdf'},
                         {'name': 'Invoices without Payment',
                          'report_name': 'account.report_invoice',
                          'report_type': 'qweb-pdf'}],
     'account.payment': [{'name': 'Payment Receipt',
                          'report_name': 'account.report_payment_receipt',
                          'report_type': 'qweb-pdf'}],
     'ir.model': [{'name': 'Model Overview',
                   'report_name': 'base.report_irmodeloverview',
                   'report_type': 'qweb-pdf'}],
     'ir.module.module': [{'name': 'Technical guide',
                           'report_name': 'base.report_irmodulereference',
                           'report_type': 'qweb-pdf'}],
     'product.packaging': [{'name': 'Product Packaging (PDF)',
                            'report_name': 'product.report_packagingbarcode',
                            'report_type': 'qweb-pdf'}],
     'product.product': [{'name': 'Pricelist',
                          'report_name': 'product.report_pricelist',
                          'report_type': 'qweb-pdf'},
                         {'name': 'Product Barcode (PDF)',
                          'report_name': 'product.report_productbarcode',
                          'report_type': 'qweb-pdf'},
                         {'name': 'Product Label (PDF)',
                          'report_name': 'product.report_productlabel',
                          'report_type': 'qweb-pdf'}],
     'product.template': [{'name': 'Product Barcode (PDF)',
                           'report_name': 'product.report_producttemplatebarcode',
                           'report_type': 'qweb-pdf'},
                          {'name': 'Product Label (PDF)',
                           'report_name': 'product.report_producttemplatelabel',
                           'report_type': 'qweb-pdf'}],
     'purchase.order': [{'name': 'Purchase Order',
                         'report_name': 'purchase.report_purchaseorder',
                         'report_type': 'qweb-pdf'},
                        {'name': 'Request for Quotation',
                         'report_name': 'purchase.report_purchasequotation',
                         'report_type': 'qweb-pdf'}],
     'res.company': [{'name': 'Preview External Report',
                      'report_name': 'web.preview_externalreport',
                      'report_type': 'qweb-pdf'},
                     {'name': 'Preview Internal Report',
                      'report_name': 'web.preview_internalreport',
                      'report_type': 'qweb-pdf'}],
     'res.partner': [{'name': 'Aged Partner Balance',
                      'report_name': 'account.report_agedpartnerbalance',
                      'report_type': 'qweb-pdf'}],
     'sale.order': [{'name': 'PRO-FORMA Invoice',
                     'report_name': 'sale.report_saleorder_pro_forma',
                     'report_type': 'qweb-pdf'},
                    {'name': 'Quotation / Order',
                     'report_name': 'sale.report_saleorder',
                     'report_type': 'qweb-pdf'}]}

To download a report::

    >>> report = odoo.report.download('account.report_invoice', [1])

The method will return a file-like object, you will have to read its content
in order to save it on your file-system::

    >>> with open('invoice.pdf', 'wb') as report_file:
    ...     report_file.write(report.read())
    ...

:ref:`Next step: Save your credentials (session) <tuto-manage-sessions>`
