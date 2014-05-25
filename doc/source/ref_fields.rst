.. _fields:

Browse object fields
====================

The table below presents the Python types returned by `OERPLib`
for each `OpenERP` fields used by ``browse_record`` objects
(see the :func:`browse <oerplib.OERP.browse>` method):

================  ==============================
`OpenERP` fields  Python types used in `OERPLib`
================  ==============================
fields.binary     basestring (str or unicode)
fields.boolean    bool
fields.char       basestring (str or unicode)
fields.date       `datetime <http://docs.python.org/library/datetime.html>`_.date
fields.datetime   `datetime <http://docs.python.org/library/datetime.html>`_.datetime
fields.float      float
fields.integer    integer
fields.selection  basestring (str or unicode)
fields.text       basestring (str or unicode)
================  ==============================

Exceptions made for relation fields:

================  ===========================================================
`OpenERP` fields  Types used in `OERPLib`
================  ===========================================================
fields.many2one   ``browse_record`` instance
fields.one2many   generator to iterate on ``browse_record`` instances 
fields.many2many  generator to iterate on ``browse_record`` instances
fields.reference  ``browse_record`` instance
================  ===========================================================

