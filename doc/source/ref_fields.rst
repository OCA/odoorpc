.. _fields:

Browse object fields
====================

The table below presents the Python types returned by `OdooRPC`
for each `Odoo` fields used by :class:`Recordset <odoorpc.models.Model>`
objects (see the :func:`browse <odoorpc.models.Model.browse>` method):

================  ==============================
`Odoo` fields     Python types used in `OdooRPC`
================  ==============================
fields.Binary     unicode or str
fields.Boolean    bool
fields.Char       unicode or str
fields.Date       `datetime <http://docs.python.org/library/datetime.html>`_.date
fields.Datetime   `datetime <http://docs.python.org/library/datetime.html>`_.datetime
fields.Float      float
fields.Integer    integer
fields.Selection  unicode or str
fields.Text       unicode or str
fields.Html       unicode or str
fields.Many2one   ``Recordset``
fields.One2many   ``Recordset``
fields.Many2many  ``Recordset``
fields.Reference  ``Recordset``
================  ==============================

