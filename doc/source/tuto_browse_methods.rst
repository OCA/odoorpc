.. _tuto-browse-methods:

Call methods from a Model or from records
*****************************************

Unlike the `Odoo` API, there is a difference between class methods
(e.g.: `create`, `search`, ...) and instance methods that apply directly on
existing records (`write`, `read`, ...)::

    >>> User = odoo.env['res.users']
    >>> User.write([1], {'name': "Dupont D."})  # Using the class method
    True
    >>> user = User.browse(1)
    >>> user.write({'name': "Dupont D."})       # Using the instance method

When a method is called directly on records, their `ids` (here `user.ids`) is
simply passed as the first parameter.
This also means that you are not able to call class methods such as `create`
or `search` from a set of records::

    >>> User = odoo.env['res.users']
    >>> User.create({...})              # Works
    >>> user = User.browse(1)
    >>> user.ids
    [1]
    >>> user.create({...})              # Error, `create()` does not accept `ids` in first parameter
    >>> user.__class__.create({...})    # Works

This is a behaviour `by design`: `OdooRPC` has no way to make the difference
between a `class` or an `instance` method through RPC, this is why it differs
from the `Odoo` API.

:ref:`Next step: Update data through records <tuto-update-browse-records>`
