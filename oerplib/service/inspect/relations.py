# -*- coding: utf-8 -*-
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

import re

from oerplib import error

TPL_MODEL = """<
<table cellborder="0" cellpadding="0" cellspacing="0"
       border="1" bgcolor="{model_bgcolor}" height="100%%">
    <tr>
        <td border="0" bgcolor="{model_bgcolor_title}" align="center" colspan="3">
            <font color="{model_color_title}">{name}</font>
        </td>
    </tr>
    {attrs}
    {relations_r}
</table>>"""

TPL_MODEL_SUBTITLE = """
<tr><td> </td></tr>
<tr>
    <td align="center"
        border="0"
        colspan="3"><font color="{color}">[{title}]</font></td>
</tr>
"""

TPL_MODEL_ATTR = """
<tr>
    <td align="left" border="0">- <font color="{color_name}">{name}</font></td>
    <td align="left" border="0">{flags}</td>
    <td align="left" border="0"> <font color="{color_name}">{type_}</font> </td>
</tr>
"""

TPL_MODEL_REL = """
<tr>
    <td align="left" border="0">- {name}</td>
    <td align="left" border="0">{flags}</td>
    <td align="left" border="0"> <font color="{color_name}">{type_}</font></td>
</tr>
"""


def pattern2regex(pattern):
    """Return a regular expression corresponding to `pattern` (simpler
    representation of the regular expression).
    """
    pattern = "^{0}$".format(pattern.replace('*', '.*'))
    return re.compile(pattern)


def match_in(elt, lst):
    """Return `True` if `elt` is matching one of a pattern in `lst`."""
    for regex in lst:
        if regex.match(elt):
            return True
    return False


class Relations(object):
    """Draw relations between models with `Graphviz`."""
    def __init__(self, oerp, models, maxdepth=1, whitelist=None, blacklist=None,
                 attrs_whitelist=None, attrs_blacklist=None, config=None):
        self.oerp = oerp
        self._models = models
        self._maxdepth = maxdepth
        self._whitelist = [pattern2regex(model) for model in (models)]
        self._whitelist.extend(
            [pattern2regex(model) for model in (whitelist or ['*'])])
        self._blacklist = [pattern2regex(model) for model in (blacklist or [])]
        self._attrs_whitelist = [pattern2regex(model)
                                 for model in (attrs_whitelist or [])]
        self._attrs_blacklist = [pattern2regex(model)
                                 for model in (attrs_blacklist or [])]
        # Configuration options
        self._config = {
            'relation_types': ['many2one', 'one2many', 'many2many'],
            'show_many2many_table': False,
            'color_many2one': '#0E2548',
            'color_one2many': '#008200',
            'color_many2many': '#6E0004',
            'model_root_bgcolor_title': '#A50018',
            'model_bgcolor_title': '#64629C',
            'model_color_title': 'white',
            'model_color_subtitle': '#3E3D60',
            'model_bgcolor': 'white',
            'color_normal': 'black',
            'color_required': 'blue',
            'color_function': '#7D7D7D',
            'space_between_models': 0.25,
        }
        self._config.update(config or {})
        # Store relations between data models:
        self._relations = {}
        self._stack = {'o2m': {}}
        # Build and draw relations for each model
        for model in models:
            self._build_relations(self.oerp.get(model), 0)

    def _build_relations(self, obj, depth):
        """Build all relations of `obj` recursively:
            - many2one
            - one2many (will be bound to the related many2one)
            - many2many (will be bound with the eventual many2many from the
              other side)
        """
        # Stop scanning when the maxdepth is reached, or when the data model
        # has already been scanned
        if obj._name in self._models:
            depth = 0
        if depth > self._maxdepth or obj._name in self._relations:
            return
        # Check the whitelist, then the blacklist
        if obj._name not in self._models:
            if self._whitelist:
                if not match_in(obj._name, self._whitelist):
                    return
            if self._blacklist:
                if match_in(obj._name, self._blacklist):
                    return
        # Only increments depth for data models which are not already scanned
        if obj._name not in self._relations:
            depth += 1
        # Scan relational fields of the data model
        fields = obj.fields_get()
        if obj._name not in self._relations:
            self._relations[obj._name] = {
                'relations': {},
                'relations_r': {},  # Recursive relations
                'fields': dict((k, v) for k, v in fields.iteritems()
                               if not v.get('relation')),
            }
        for name, data in fields.iteritems():
            if 'relation' in data \
                    and data['type'] in self._config['relation_types']:
                rel = data['relation']
                # where to store the relation?
                store_type = obj._name == rel and 'relations_r' or 'relations'
                # flags
                flags = {
                    'required': data.get('required'),
                    'function': data.get('function'),
                    'fnct_inv': data.get('fnct_inv'),
                    'fnct_search': data.get('fnct_search'),
                }
                # many2one
                if data['type'] == 'many2one':
                    # Check if related one2many fields have been registered
                    # for the current many2one relation
                    o2m_fields = obj._name in self._stack['o2m'] \
                        and rel in self._stack['o2m'][obj._name] \
                        and name in self._stack['o2m'][obj._name][rel] \
                        and self._stack['o2m'][obj._name][rel][name] \
                        or []
                    # Add the field
                    self._relations[obj._name][store_type][name] = {
                        'type': 'many2one',
                        'relation': rel,
                        'name': name,
                        'o2m_fields': o2m_fields,
                    }
                    self._relations[obj._name][store_type][name].update(flags)
                # one2many
                elif data['type'] == 'one2many':
                    # 'relation_field' key may be missing for 'one2many'
                    # generated by 'fields.function'
                    rel_f = data.get('relation_field', None)
                    # If it is a normal o2m field (with a relation field), it
                    # will be attached to its corresponding m2o field
                    if rel_f:
                        # Case where the related m2o field has already been
                        # registered
                        if rel in self._relations \
                                and rel_f in self._relations[rel][store_type]:
                            if name not in self._relations[
                                    rel][store_type][rel_f]:
                                self._relations[
                                    rel][store_type][
                                        rel_f]['o2m_fields'].append(name)
                        # Otherwise, we will process the field later (when the
                        # m2o field will be scanned)
                        else:
                            if rel not in self._stack['o2m']:
                                self._stack['o2m'][rel] = {}
                            if obj._name not in self._stack['o2m'][rel]:
                                self._stack['o2m'][rel][obj._name] = {}
                            if rel_f not in self._stack['o2m'][rel][obj._name]:
                                self._stack['o2m'][rel][obj._name][rel_f] = []
                            self._stack[
                                'o2m'][rel][obj._name][rel_f].append(name)
                    # If the o2m field has no relation field available
                    # (calculated by a function, or a related field) the
                    # relation is stored as a standalone one2many
                    else:
                        self._relations[obj._name][store_type][name] = {
                            'type': 'one2many',
                            'relation': rel,
                            'name': name,
                        }
                        self._relations[obj._name][store_type][name].update(
                            flags)
                # many2many
                elif data['type'] == 'many2many':
                    #rel_columns = data.get('related_columns') \
                    #    or data.get('m2m_join_columns')
                    #rel_columns = rel_columns and tuple(rel_columns) or None
                    self._relations[obj._name][store_type][name] = {
                        'type': 'many2many',
                        'relation': rel,
                        'name': name,
                        'third_table':
                        data.get('third_table') or data.get('m2m_join_table'),
                        'related_columns': None,
                    }
                    self._relations[obj._name][store_type][name].update(flags)
                # Scan relations recursively
                rel_obj = self.oerp.get(rel)
                self._build_relations(rel_obj, depth)

    def make_dot(self):
        """Returns a `pydot.Dot` object representing relations between models.

            >>> graph = oerp.inspect.relations(['res.partner'])
            >>> graph.make_dot()
            <pydot.Dot object at 0x2bb0650>

        See the `pydot <http://code.google.com/p/pydot/>`_ documentation
        for details.
        """
        try:
            import pydot
        except ImportError:
            raise error.InternalError("'pydot' module not found")
        output = pydot.Dot(
            graph_type='digraph', overlap='scalexy', splines='true',
            nodesep=str(self._config['space_between_models']))
        for model, data in self._relations.iteritems():
            # Generate attributes of the model
            attrs_ok = False
            attrs = []
            if self._attrs_whitelist \
                    and match_in(model, self._attrs_whitelist):
                attrs_ok = True
            if self._attrs_blacklist \
                    and match_in(model, self._attrs_blacklist):
                attrs_ok = False
            if attrs_ok:
                subtitle = TPL_MODEL_SUBTITLE.format(
                    color=self._config['model_color_subtitle'],
                    title="Attributes")
                attrs.append(subtitle)
                for k, v in sorted(data['fields'].iteritems()):
                    color_name = self._config['color_normal']
                    if v.get('function'):
                        color_name = self._config['color_function']
                    if v.get('fnct_inv'):
                        color_name = self._config['color_normal']
                    #if v.get('required'):
                    #    color_name = self._config['color_required']
                    attr = TPL_MODEL_ATTR.format(
                        name=k, type_=v['type'],
                        color_name=color_name,
                        flags=self._generate_flags_label(v))
                    attrs.append(attr)
            # Generate recursive relations of the model
            relations_r = []
            if data['relations_r']:
                subtitle = TPL_MODEL_SUBTITLE.format(
                    color=self._config['model_color_subtitle'],
                    title="Recursive relations")
                relations_r.append(subtitle)
            for data2 in data['relations_r'].itervalues():
                label = self._generate_relation_label(data2)
                flags = self._generate_flags_label(data2)
                rel_r = TPL_MODEL_REL.format(
                    name=label, flags=flags,
                    color_name=self._config['color_normal'],
                    type_=data2['type'])
                relations_r.append(rel_r)
            # Generate the layout of the model
            model_bgcolor_title = self._config['model_bgcolor_title']
            if model in self._models:
                model_bgcolor_title = self._config['model_root_bgcolor_title']
            tpl = TPL_MODEL.format(
                model_color_title=self._config['model_color_title'],
                model_bgcolor_title=model_bgcolor_title,
                model_bgcolor=self._config['model_bgcolor'],
                name=model,
                attrs=''.join(attrs),
                relations_r=''.join(relations_r))
            # Add the model to the graph
            node = self._create_node(model, 'relation', tpl)
            output.add_node(node)
            # Draw relations of the model
            for data2 in data['relations'].itervalues():
                if data2['relation'] in self._relations:
                    edge = self._create_edge(model, data2['relation'], data2)
                    output.add_edge(edge)
        return output

    def _create_node(self, name, type_, tpl=None):
        """Generate a `pydot.Node` object.
        `type_` can take one of these values: ``relation``, ``m2m_table``.
        If a HTML `tpl` is supplied, it will be used as layout for the node.
        """
        import pydot
        types = {
            'relation': {
                'margin': '0',
                'shape': tpl and 'none' or 'record',
                'label': tpl or name,
            },
            'm2m_table': {
                'margin': '0',
                'shape': tpl and 'none' or 'record',
                'color': self._config['color_many2many'],
                'fontcolor': self._config['color_many2many'],
                'label': tpl or name,
            },
        }
        return pydot.Node(name, **types[type_])

    def _create_edge(self, model1, model2, data):
        """Generate a `pydot.Edge` object, representing a relation between
        `model1` and `model2`.
        """
        import pydot
        label = self._generate_relation_label(data, space=6, on_arrow=True)
        return pydot.Edge(
            model1, model2,
            label=label,
            labeldistance='10.0',
            color=self._config['color_{0}'.format(data['type'])],
            fontcolor=self._config['color_{0}'.format(data['type'])])
            #arrowhead=(data['type'] == 'many2many' and 'none' or 'normal'),

    def _generate_flags_label(self, data):
        """Generate a HTML label for status flags of a field
        described by `data`.
        """
        flags = []
        if data.get('required'):
            flags.append("<font color='{color}'>R</font>".format(
                color=self._config['color_required']))
        if data.get('function'):
            name = data.get('fnct_inv') and "Fw" or "F"
            if data.get('fnct_search'):
                name += "s"
            flags.append("<font color='{color}'>{name}</font>".format(
                name=name, color=self._config['color_function']))
        if flags:
            return " &#91;{0}&#93;".format(' '.join(flags))
        return ""

    def _generate_relation_label(self, data, space=0, on_arrow=False):
        """Generate a HTML label based for the relation described by `data`."""
        name_color = self._config['color_{0}'.format(data['type'])]
        label = "{space}<font color='{color}'>{name}</font>".format(
            color=name_color, name=data['name'], space=' ' * space)
        # many2one arrow
        if data['type'] == 'many2one' and data['o2m_fields']:
            label = "{label} <font color='{color}'>← {o2m}</font>".format(
                label=label,
                color=self._config['color_one2many'],
                o2m=', '.join(data['o2m_fields']))
        # one2many "standalone" arrow
        if data['type'] == 'one2many':
            pass
        # many2many arrow
        if data['type'] == 'many2many':
            m2m_table = ''
            if self._config['show_many2many_table']:
                if data.get('third_table'):
                    m2m_table = '({table})'.format(
                        table=data.get('third_table'))
            label = "{space}<font color='{color}'>{name} {m2m_t}</font>".format(
                color=name_color, name=data['name'],
                m2m_t=m2m_table, space=' ' * space)
        # flags
        if on_arrow:
            label += self._generate_flags_label(data)
        # add space on the right
        label = label + "{space}".format(space=' ' * space)
        # closing tag
        if on_arrow:
            label = "<{label}>".format(label=label)
        return label

    def write(self, *args, **kwargs):
        """Write the resulting graph in a file.
        It is just a wrapper around the :func:`pydot.Dot.write` method
        (see the `pydot <http://code.google.com/p/pydot/>`_ documentation for
        details).  Below a common way to use it::

            >>> graph = oerp.inspect.relations(['res.partner'])
            >>> graph.write('relations_res_partner.png', format='png')

        About supported formats, consult the
        `Graphviz documentation <http://www.graphviz.org/doc/info/output.html>`_.
        """
        output = self.make_dot()
        return output.write(*args, **kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
