# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "OdooRPC"
copyright = "2014, Sébastien Alix"
author = "Sébastien Alix"
release = "0.11.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
]

doctest_global_setup = """
import os
PROTOCOL = os.environ.get('ORPC_TEST_PROTOCOL', 'jsonrpc')
HOST = os.environ.get('ORPC_TEST_HOST', 'localhost')
PORT = os.environ.get('ORPC_TEST_PORT', 8069)
DB = os.environ.get('ORPC_TEST_DB', 'odoorpc_doctest')
USER = os.environ.get('ORPC_TEST_USER', 'admin')
PWD = os.environ.get('ORPC_TEST_PWD', 'admin')
VERSION = os.environ.get('ORPC_TEST_VERSION', '10.0')
SUPER_PWD = os.environ.get('ORPC_TEST_SUPER_PWD', 'admin')
import odoorpc
from odoorpc.tools import v
odoo = odoorpc.ODOO(HOST, protocol=PROTOCOL, port=PORT, version=VERSION)
# == create a database
if DB not in odoo.db.list():
    odoo.db.create(SUPER_PWD, DB, True)
odoo.login(DB, USER, PWD)
# == install fr_FR language
Wizard = odoo.env['base.language.install']
lang_code = 'fr_FR'
if v(odoo.version)[0] >= 16:
    lang_ids = odoo.env['res.lang'].with_context(active_test=False).search(
        [('code', '=', lang_code)]
    )
    values = {'lang_ids': [(6, 0, lang_ids)]}
else:
    values = {'lang': lang_code}
wiz_id = Wizard.create(values)
Wizard.lang_install([wiz_id])
# == install some modules
odoo.config['timeout'] = 600
Module = odoo.env['ir.module.module']
module_ids = Module.search([('name', 'in', ['sale', 'crm']), ('state', '=', 'uninstalled')])
if module_ids:
    Module.button_immediate_install(module_ids)
odoo.config['timeout'] = 120
"""

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_static_path = ["_static"]

html_theme = "nature"
html_style = "odoorpc.css"
html_logo = "_static/logo.png"
