#!/usr/bin/env python
"""A sample script to demonstrate some of functionalities of OERPLib."""
import oerplib

# XMLRPC server configuration (NETRPC is also supported)
SERVER = 'localhost'
PROTOCOL = 'xmlrpc'
PORT = 8069
# Name of the OpenERP database to use
DATABASE = 'db_name'

USER = 'admin'
PASSWORD = 'password'

try:
    # Login
    oerp = oerplib.OERP(
        server=SERVER, database=DATABASE, protocol=PROTOCOL, port=PORT)
    oerp.login(USER, PASSWORD)

    # ----------------------- #
    # -- Low level methods -- #
    # ----------------------- #

    # Execute - search
    user_ids = oerp.execute('res.users', 'search', [('id', '=', oerp.user.id)])
    # Execute - read
    user_data = oerp.execute('res.users', 'read', user_ids[0])
    # Execute - write
    oerp.execute('res.users', 'write', user_ids[0], {'name': "Administrator"})
    # Execute - create
    new_user_id = oerp.execute('res.users', 'create', {'login': "New user"})

    # --------------------- #
    # -- Dynamic methods -- #
    # --------------------- #

    # Get the model
    user_obj = oerp.get('res.users')
    # Search IDs of a model that match criteria
    user_obj.search([('name', 'ilike', "Administrator")])
    # Create a record
    new_user_id = user_obj.create({'login': "new_user"})
    # Read data of a record (just the name field)
    user_data = user_obj.read([new_user_id], ['name'])
    # Write a record
    user_obj.write([new_user_id], {'name': "New user"})
    # Delete a record
    user_obj.unlink([new_user_id])

    # -------------------- #
    # -- Browse objects -- #
    # -------------------- #

    # Browse an object
    user = user_obj.browse(oerp.user.id)
    print(user.name)
    print(user.company_id.name)
    # .. or many objects
    order_obj = oerp.get('sale.order')
    for order in order_obj.browse([68, 69]):
        print(order.name)
        print(order.partner_id.name)
        for line in order.order_line:
            print('\t{0}'.format(line.name))

    # ----------------------- #
    # -- Download a report -- #
    # ----------------------- #

    so_pdf_path = oerp.report('sale.order', 'sale.order', 1)
    inv_pdf_path = oerp.report('webkitaccount.invoice', 'account.invoice', 1)

    # ------------------------- #
    # -- Databases management-- #
    # ------------------------- #

    # List databases
    print(oerp.db.list())
    # Create a database in background
    oerp.db.create(
        'super_admin_passwd', 'my_db',
        demo_data=True, lang='fr_FR',
        admin_passwd='admin_passwd')
    # ... after a while, dump it
    my_dump = oerp.db.dump('super_admin_password', 'my_db')
    # Create a new database from the dump
    oerp.db.restore('super_admin_password', 'my_new_db', my_dump)
    # Delete the old one
    oerp.db.drop('super_admin_password', 'my_db')

except oerplib.error.Error as e:
    print(e)
except Exception as e:
    print(e)
