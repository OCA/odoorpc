oerplib
=======

.. automodule:: oerplib
    :members:

Here's a sample session using this module::

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')                    # connect to localhost, default port
    >>> user = oerp.login('admin', 'admin', 'my_database')  # login returns an user object
    >>> user.name
    'Administrator'
    >>> oerp.save('foo')                                    # save session informations in ~/.oerplibrc
    >>> oerp = oerplib.load('foo')                          # get a pre-configured session from ~/.oerplibrc
