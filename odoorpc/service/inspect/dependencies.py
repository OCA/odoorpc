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
"""Implements the :class:`Dependencies` class used to compute dependencies
between server modules.
"""
import copy

from oerplib import error
from oerplib.tools import v

TPL_MODULE = """<
<table cellborder="0" cellpadding="0" cellspacing="0"
       border="1" bgcolor="{module_bgcolor}" height="100%%">
    <tr>
        <td border="0" bgcolor="{module_bgcolor_title}" align="center">
            <font color="{module_color_title}">{name}</font>
        </td>
    </tr>
    {models}
    {comment}
</table>>"""

TPL_MODULE_MODEL = """
<tr>
    <td align="left" border="0">- <font color="{color_model}">{model}</font></td>
</tr>
"""

TPL_MODULE_COMMENT = """
<tr>
    <td align="center" border="0"><font color="{module_color_comment}">{comment}</font></td>
</tr>
"""


def pattern2oerp(pattern):
    """Return a SQL expression corresponding to `pattern` (simpler
    representation of the SQL string matching).
    """
    return pattern.replace('*', '%')


class Dependencies(object):
    """Draw dependencies between modules. Models can be displayed in their
    respecting modules as well.
    """
    def __init__(self, oerp, modules=None, models=None, models_blacklist=None,
                 restrict=False, config=None):
        self.oerp = oerp
        self._restrict = restrict
        self._root_modules = modules or []
        # Configuration options
        self._config = {
            'module_uninst_bgcolor_title': '#DEDFDE',
            'module_uninst_color_title': 'black',
            'module_inst_bgcolor_title': '#64629C',
            'module_inst_color_title': 'white',
            'module_root_bgcolor_title': '#A50018',
            'module_root_color_title': 'white',
            'module_highlight_bgcolor_title': '#1F931F',
            'module_highlight_color_title': 'white',
            'module_bgcolor': 'white',
            'module_color_comment': 'grey',
            'model_color_normal': 'black',
            'model_color_transient': '#7D7D7D',
            'show_module_inst': True,
            'show_module_uninst': False,
            'show_model_normal': True,
            'show_model_transient': False,
        }
        self._config.update(config or {})
        # Check if root modules exist
        self._check_root_modules()
        # List of data models
        self._models = self._get_models_data(
            models or [], models_blacklist or [])
        # List of modules computed according to the `restrict` parameter
        # (display all modules or only modules related to data models)
        self._modules, self._modules_full = self._get_modules(
            self._models, keep=not bool(self._root_modules))
        # Fetch dependencies between modules
        self._scan_module_dependencies()

    #@property
    #def models(self):
    #    """Returns a dictionary of all models used to draw the graph."""
    #    return self._models

    #@property
    #def modules(self):
    #    """Returns a dictionary of all modules used to draw the graph."""
    #    return self._modules

    def _check_root_modules(self):
        """Check if `root` modules exist, raise an error if not."""
        module_obj = self.oerp.get('ir.module.module')
        for module in self._root_modules:
            if not module_obj.search([('name', 'ilike', module)]):
                raise error.InternalError(
                    "'{0}' module does not exist".format(module))

    def _get_models_data(self, models, models_blacklist):
        """Returns a dictionary `{MODEL: DATA, ...}` of models corresponding to
        `models - models_blacklist` patterns (whitelist substracted
        by a blacklist).
        """
        res = {}
        # OpenERP v5 does not have the 'modules' field on 'ir.model' used to
        # bound a data model and its related modules.
        if v(self.oerp.version) <= v('6.0'):
            return res
        models_patterns = \
            [pattern2oerp(model) for model in (models)]
        models_blacklist_patterns = \
            [pattern2oerp(model) for model in (models_blacklist)]
        if models:
            model_obj = self.oerp.get('ir.model')
            args = [('model', '=ilike', model)
                    for model in models_patterns]
            for _ in range(len(args) - 1):
                args.insert(0, '|')
            for model in models_blacklist_patterns:
                args.append('!')
                args.append(('model', '=ilike', model))
            ids = model_obj.search(args)
            for data in model_obj.read(ids, ['model', 'modules', 'osv_memory']):
                if not self._config['show_model_transient'] \
                        and data['osv_memory']:
                    continue
                if not self._config['show_model_normal'] \
                        and not data['osv_memory']:
                    continue
                res[data['model']] = {
                    'model': data['model'],
                    'modules': data['modules']
                    and data['modules'].split(', ') or [],
                    'transient': data['osv_memory'],
                }
        return res

    def _get_modules(self, models=None, keep=False):
        """Returns a dictionary `{MODULE: DATA, ...}` with all modules installed
        (`restrict=False`) or only with modules related to data models
        (`restrict=True`).
        """
        if models is None:
            models = {}
        modules = {}
        modules_full = {}
        # Fetch all the modules installed on the server
        module_obj = self.oerp.get('ir.module.module')
        states_inst = ['installed', 'to upgrade', 'to remove']
        states_uninst = ['uninstalled', 'uninstallable', 'to install']
        states = []
        if self._config['show_module_inst'] \
                and not self._config['show_module_uninst']:
            states = states_inst[:]
        elif not self._config['show_module_inst'] \
                and self._config['show_module_uninst']:
            states = states_uninst[:]
        elif self._config['show_module_inst'] \
                and self._config['show_module_uninst']:
            states = []
        args = states and [('state', 'in', states)] or []
        module_ids = module_obj.search(args)
        for data in module_obj.read(module_ids, ['name', 'state']):
            modules_full[data['name']] = {
                'models': [],
                'depends': [],
                'keep': keep,
                'installed': data['state'] in states_inst
            }
        # Dispatch data models in their related modules
        for model, data in models.iteritems():
            for module in data['modules']:
                if module in modules_full \
                        and model not in modules_full[module]['models']:
                    modules_full[module]['models'].append(model)
        # Compute the list of modules related to data models
        if self._restrict:
            for model, data in models.iteritems():
                for module in data['modules']:
                    if module not in modules:
                        modules[module] = {
                            'models': [],
                            'depends': [],
                            'keep': keep,
                            'installed': modules_full[module]['installed'],
                        }
                    if model not in modules[module]['models']:
                        modules[module]['models'].append(model)
            # Root modules are included by default, even if they don't contain
            # any of the matching models
            for module in self._root_modules:
                if module not in modules:
                    modules[module] = {
                        'models': [],
                        'depends': [],
                        'keep': keep,
                        'installed': modules_full[module]['installed'],
                    }
        # Otherwise, just take the full list of modules
        else:
            modules = copy.deepcopy(modules_full)
        return modules, modules_full

    def _scan_module_dependencies(self):
        """Scan dependencies of modules, until reaching each node in
        `root_modules`.  If `root_modules` is empty, dependencies of all
        installed modules will be computed.
        """
        module_obj = self.oerp.get('ir.module.module')
        # Compute dependencies of all installed modules
        for name in self._modules_full:
            module_ids = module_obj.search([('name', '=', name)])
            module = module_obj.browse(module_ids[0])
            for dependency in module.dependencies_id:
                if dependency.name in self._modules_full:
                    self._modules_full[name]['depends'].append(dependency.name)
                if name in self._modules and dependency.name in self._modules:
                    self._modules[name]['depends'].append(dependency.name)
        # In restrict mode, fix modules similar to "root" module (with no direct
        # dependency) while they may have indirect dependencies
        if self._restrict:
            for name, data in self._modules.items():  # Avoid iter modification
                # Detect fake "root" module
                if not data['depends'] and self._modules_full[name]['depends']:
                    self._fix_fake_root_module(name)
        # Mark modules to keep in the graph if they belong to a path
        # leading to one of the root modules
        for module in self._modules:
            queue = []
            queue.append(module)
            # If the module is a root module, we keep it regardless of its
            # dependencies
            if module in self._root_modules:
                self._modules[module]['keep'] = True
            # Recursive function to scan the graph and keep modules
            def process_keep(queue, module):
                for depend in self._modules[module]['depends']:
                    queue.append(depend)
                    # Found? Keep modules concerned by this path
                    if depend in self._root_modules:
                        for mod in queue:
                            self._modules[mod]['keep'] = True
                        break
                    else:
                        process_keep(queue, depend)
                queue.pop()
            process_keep(queue, module)

    def _fix_fake_root_module(self, module):
        """Fix the fake root `module` by finding its indirect dependencies."""
        known_paths = []

        def find_path(path, mod, common_model):
            """Try to found a path from the module `mod` among all installed
            modules to reach any 'restricted' module.
            """
            if set(path) not in known_paths:
                known_paths.append(set(path))
            path.append(mod)
            for depend in self._modules_full[mod]['depends']:
                path.append(depend)
                if set(path) in known_paths:
                    continue
                if depend in self._modules:
                    if common_model:
                        # Has the 'head' module a common data model with
                        # the 'tail' one?
                        mod_tail = self._modules[module]['models']
                        mod_head = self._modules[depend]['models']
                        if list(set(mod_tail) & set(mod_head)):
                            return True
                    else:
                        return True
                path.pop()
                res = find_path(path, depend, common_model)
                if res:
                    return res
            path.pop()
            return False

        path = []
        # Modules in the path should preferably have a common data model
        found_ok = find_path(path, module, common_model=True)
        # If not, we try again without the rule of the common model
        if not found_ok:
            known_paths = []
            path = []
            found_ok = find_path(path, module, common_model=False)
        # Update the graph by adding required modules to satisfy the
        # indirect dependency
        if found_ok:
            for index, mod in enumerate(path):
                if mod not in self._modules:
                    # Add the required module, but without its dependencies
                    self._modules[mod] = copy.deepcopy(self._modules_full[mod])
                    for depend in self._modules[mod]['depends'][:]:
                        if depend not in self._modules:
                            self._modules[mod]['depends'].remove(depend)
                    self._modules[mod]['comment'] = \
                        "Indirect dependency"
                    # Add the current module as a dependency to the previous one
                    previous_mod = path[index - 1]
                    if mod not in self._modules[previous_mod]['depends']:
                        self._modules[previous_mod]['depends'].append(mod)

    @staticmethod
    def _draw_graph_node(module, tpl):
        """Generates a Graphviz node named `module`."""
        import pydot
        return pydot.Node(module, margin='0', shape='none', label=tpl)

    @staticmethod
    def _draw_graph_edge(parent, child):
        """Generates a Graphviz edge between `parent` and `child` modules."""
        import pydot
        return pydot.Edge( parent, child, dir='back')

    def make_dot(self):
        """Returns a `pydot.Dot` object representing dependencies
        between modules.

            >>> graph = oerp.inspect.dependencies(['base'], ['res.partner'])
            >>> graph.make_dot()
            <pydot.Dot object at 0x2f01990>

        See the `pydot <http://code.google.com/p/pydot/>`_ documentation
        for details.
        """
        try:
            import pydot
        except ImportError:
            raise error.InternalError("'pydot' module not found")
        output = pydot.Dot()

        def get_template(module, data):
            """Generate the layout of the module."""
            root = all(not self._modules[depend]['keep']
                       for depend in data['depends'])
            # Model lines
            tpl_models = []
            for model in sorted(data['models']):
                color_model = self._config['model_color_normal']
                if self._models[model]['transient']:
                    color_model = self._config['model_color_transient']
                tpl_models.append(
                    TPL_MODULE_MODEL.format(
                        color_model=color_model, model=model))
            # Module comment
            tpl_comment = None
            if data.get('comment'):
                tpl_comment = "<tr><td> </td></tr>"
                tpl_comment += TPL_MODULE_COMMENT.format(
                    module_color_comment=self._config['module_color_comment'],
                    comment=data['comment'])
            # Module
            module_color_title = self._config['module_inst_color_title']
            module_bgcolor_title = self._config['module_inst_bgcolor_title']
            if root:
                module_color_title = self._config['module_root_color_title']
                module_bgcolor_title = self._config['module_root_bgcolor_title']
            if not root and tpl_models:
                module_color_title = \
                    self._config['module_highlight_color_title']
                module_bgcolor_title = \
                    self._config['module_highlight_bgcolor_title']
            if not data.get('installed'):
                module_color_title = self._config['module_uninst_color_title']
                module_bgcolor_title = \
                    self._config['module_uninst_bgcolor_title']
            tpl = TPL_MODULE.format(
                module_color_title=module_color_title,
                module_bgcolor_title=module_bgcolor_title,
                module_bgcolor=self._config['module_bgcolor'],
                name=module.lower(),
                models=''.join(tpl_models),
                comment=tpl_comment or '')
            return tpl

        for module, data in self._modules.iteritems():
            if not data['keep']:
                continue
            # Add the module as node
            tpl = get_template(module, data)
            node = self._draw_graph_node(module, tpl)
            output.add_node(node)
            for dependency in data['depends']:
                if not self._modules[dependency]['keep']:
                    continue
                # Add edge between the module and it's dependency
                edge = self._draw_graph_edge(dependency, module)
                output.add_edge(edge)

        return output

    def write(self, *args, **kwargs):
        """Write the resulting graph in a file.
        It is just a wrapper around the :func:`pydot.Dot.write` method
        (see the `pydot <http://code.google.com/p/pydot/>`_ documentation for
        details).  Below a common way to use it::

            >>> graph = oerp.inspect.dependencies(['base'], ['res.partner'])
            >>> graph.write('dependencies_res_partner.png', format='png')
        
        About supported formats, consult the
        `Graphviz documentation <http://www.graphviz.org/doc/info/output.html>`_.
        """
        output = self.make_dot()
        return output.write(*args, **kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
