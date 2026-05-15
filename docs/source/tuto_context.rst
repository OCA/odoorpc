.. _tuto-context:

Change the user's context
*************************

`Odoo` uses the user's context to adapt the results of some queries like:
   - reading/updating the translatable fields (english, french...),
   - reading/updating the date fields following the user's timezone
   - change the behavior of a method/query according to the context keys

Global context
''''''''''''''

Changing this context can be done globally by updating the
:func:`context <odoorpc.env.Environment.context>`:

.. doctest::

   >>> odoo.env.context['lang'] = 'en_US'
   >>> odoo.env.context['tz'] = 'Europe/Paris'

From now all queries will be performed with the above updated context.

Model/recordset context
'''''''''''''''''''''''

The context can also be updated punctually with the
:func:`with_context <odoorpc.models.Model.with_context>` method on a model or
a recordset (without impacting the global context).
For instance to update translations of a recordset:

.. doctest::

   >>> Product = odoo.env['product.product']
   >>> product_en = Product.browse(1)
   >>> product_en.env.lang
   'en_US'
   >>> product_en.name = "My product"  # Update the english translation
   >>> product_fr = product_en.with_context(lang='fr_FR')
   >>> product_fr.env.lang
   'fr_FR'
   >>> product_fr.name = "Mon produit" # Update the french translation

Or to retrieve all records (visible records and archived ones):

.. doctest::

   >>> all_product_ids = Product.with_context(active_test=False).search([])


:ref:`Next step: Download reports <tuto-download-report>`
