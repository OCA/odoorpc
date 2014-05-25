# -*- coding: UTF-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2013 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""Provides the :func:`scan_on_change` function."""
import xml.etree.ElementTree
import re

ON_CHANGE_RE = re.compile('^(.*?)\((.*)\)$')


def scan_on_change(oerp, models):
    """Scan all `on_change` methods detected among views of `models`."""
    result = {}
    view_obj = oerp.get('ir.ui.view')
    model_data_obj = oerp.get('ir.model.data')
    for model in models:
        # Get all model views
        view_ids = view_obj.search(
            [('model', '=', model), ('type', 'in', ['form', 'tree'])])
        model_data_ids = model_data_obj.search(
            [('res_id', 'in', view_ids), ('model', '=', 'ir.ui.view')])
        model_data = model_data_obj.read(
            model_data_ids, ['name', 'module', 'res_id'])
        for data in model_data:
            # For each view, find all `on_change` methods
            view_name = "{0}.{1}".format(data['module'], data['name'])
            view_data = oerp.execute(
                model, 'fields_view_get', data['res_id'], 'form')
            _scan_view(model, view_name, view_data, result)
    return result


def _scan_view(model, view_name, view_data, result):
    """Update `result` with all `on_change` methods detected
    on the view described by `view_data`.
    """
    if model not in result:
        result[model] = {}
    # Scan the main view description
    xml_root = xml.etree.ElementTree.fromstring(view_data['arch'])
    # NOTE: Python 2.6 does not support full XPath, it is
    # why the ".//field" pattern is used instead of ".//field[@on_change]"
    for elt in xml_root.findall(".//field"):
        if 'on_change' not in elt.attrib:
            continue
        match = ON_CHANGE_RE.match(elt.attrib['on_change'])
        if match:
            func = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(',')]
            field = elt.attrib['name']
            if func not in result[model]:
                result[model][func] = {}
            if view_name not in result[model][func]:
                result[model][func][view_name] = {}
            if field not in result[model][func][view_name]:
                result[model][func][view_name][field] = []
            if args and args not in result[model][func][view_name][field]:
                args = map(_clean_arg, args)
                result[model][func][view_name][field] = args
    # Scan recursively all other sub-descriptions defined in the view
    for field_name, field_data in view_data['fields'].iteritems():
        if field_data.get('views') and field_data['views'].get('form'):
            model = field_data['relation']
            if field_data['views'].get('form'):
                _scan_view(
                    model, view_name, field_data['views']['form'], result)
            if field_data['views'].get('tree'):
                _scan_view(
                    model, view_name, field_data['views']['tree'], result)
    return result


def _clean_arg(arg):
    return {
        'False': False,
        'True': True,
        'None': None,
    }.get(arg, arg)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
