#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import setuptools

name = 'OdooRPC'
version = '0.6.2'
description = ("OdooRPC is a Python package providing an easy way to "
               "pilot your Odoo servers through RPC.")
with open("README.rst", "r") as readme:
    long_description = readme.read()
keywords = ("openerp odoo server rpc client xml-rpc xmlrpc jsonrpc json-rpc "
            "odoorpc oerplib communication lib library python "
            "service web webservice")
author = "Sebastien Alix"
author_email = 'seb@usr-src.org'
url = 'https://github.com/OCA/odoorpc'
license = 'LGPL v3'
doc_build_dir = 'doc/build'
doc_source_dir = 'doc/source'

cmdclass = {}
command_options = {}
# 'build_doc' option
try:
    from sphinx.setup_command import BuildDoc
    if not os.path.exists(doc_build_dir):
        os.mkdir(doc_build_dir)
    cmdclass.update({'build_doc': BuildDoc})
    command_options.update({
        'build_doc': {
            #'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', version),
            'source_dir': ('setup.py', doc_source_dir),
            'build_dir': ('setup.py', doc_build_dir),
            'builder': ('setup.py', 'html'),
        }})
except Exception:
    print("No Sphinx module found. You have to install Sphinx "
          "to be able to generate the documentation.")

setuptools.setup(name=name,
      version=version,
      description=description,
      long_description=long_description,
      long_description_content_type="text/x-rst",
      keywords=keywords,
      author=author,
      author_email=author_email,
      url=url,
      packages=['odoorpc',
                'odoorpc.rpc'],
      license=license,
      cmdclass=cmdclass,
      command_options=command_options,
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Odoo",
      ],
      )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
