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
"""Provide the :class:`Inspect` class which can output useful server data.

oerplib.service.inspect.Inspect
'''''''''''''''''''''''''''''''
"""
from functools import wraps

from oerplib import error


class Inspect(object):
    """.. versionadded:: 0.8

    The `Inspect` class provides methods to output useful server data.

    .. note::
        This service have to be used through the :attr:`oerplib.OERP.inspect`
        property.

    >>> import oerplib
    >>> oerp = oerplib.OERP('localhost')
    >>> user = oerp.login('admin', 'passwd', 'database')
    >>> oerp.inspect
    <oerplib.service.inspect.Inspect object at 0xb42fa84f>

    .. automethod:: relations(models, maxdepth=1, whitelist=['*'], blacklist=[], attrs_whitelist=[], attrs_blacklist=[], config={})

        Return a :class:`Relations <oerplib.service.inspect.relations.Relations>`
        object containing relations between data models, starting from `models`
        (depth = 0) and iterate recursively until reaching the `maxdepth` limit.

        `whitelist` and `blacklist` of models can be defined with patterns
        (a joker ``*`` can be used to match several models like ``account*``).
        The whitelist has a lower priority than the blacklist, and all models
        declared in `models` are automatically integrated to the `whitelist`.

        In the same way, displaying attributes can be defined for each model
        with ``attrs_whitelist`` and ``attrs_blacklist``. By default, model
        attributes are not displayed, unless the ``'*'`` pattern is supplied in
        ``attrs_whitelist``, or if only the ``attrs_blacklist`` is defined.

            >>> oerp.inspect.relations(
            ...     ['res.users'],
            ...     maxdepth=1,
            ...     whitelist=['res*'],
            ...     blacklist=['res.country*'],
            ...     attrs_whitelist=['*'],
            ...     attrs_blacklist=['res.partner', 'res.company'],
            ... ).write('res_users.png', format='png')

        `config` is a dictionary of options to override some attributes of
        the graph. Here the list of options and their default values:

            - ``relation_types: ['many2one', 'one2many', 'many2many']``,
            - ``show_many2many_table: False``,
            - ``color_many2one: #0E2548``,
            - ``color_one2many: #008200``,
            - ``color_many2many: #6E0004``,
            - ``model_root_bgcolor_title: #A50018``,
            - ``model_bgcolor_title: #64629C``,
            - ``model_color_title: white``,
            - ``model_color_subtitle': #3E3D60``,
            - ``model_bgcolor: white``,
            - ``color_normal: black``,
            - ``color_required: blue``
            - ``color_function: #D9602E``
            - ``space_between_models: 0.25``,

        >>> oerp.inspect.relations(
        ...     ['res.users'],
        ...     config={'relation_types': ['many2one']},  # Only show many2one relations
        ... ).write('res_users.png', format='png')

        .. note::
            With `OpenERP` < `6.1`, `many2one` and `one2many` relationships can
            not be bound together. Hence, a `one2many` relationship based on a
            `many2one` will draw a separate arrow.


    .. automethod:: dependencies(modules=[], models=[], models_blacklist=[], restrict=False, config={})

        Return a :class:`Dependencies <oerplib.service.inspect.dependencies.Dependencies>`
        object describing dependencies between modules. The `modules` defines
        a list of root nodes to reach among all dependencies (modules not
        related to them are not displayed). The default behaviour is to compute
        all dependencies between installed modules. The `models` list can be
        used to display all matching models among computed dependencies.

        `models` and `models_blacklist` parameters can be defined with patterns
        (a joker ``*`` can be used to match several models like ``account*``).
        The whitelist (`models`) has a lower priority than the blacklist
        (`models_blacklist`)::

            >>> oerp.inspect.dependencies(
            ...     models=['res.partner*'],
            ...     models_blacklist=['res.partner.title', 'res.partner.bank'],
            ... ).write('dependencies_res_partner.png', format='png')

        By default all installed modules are shown on the graph. To limit the
        result to modules related to the `base` one (its childs)::

            >>> oerp.inspect.dependencies(
            ...     ['base'],
            ...     ['res.partner*'],
            ...     ['res.partner.title', 'res.partner.bank'],
            ... ).write('dependencies_res_partner_base.png', format='png')

        All modules related to `base` are shown on the resulting graph, and
        matching models are highlighted among them, but some modules remain
        empty.
        To hide these "noisy" modules and restrict the resulting graph to
        data models that interest you, add the ``restrict=True`` parameter::

            >>> oerp.inspect.dependencies(
            ...     ['base'],
            ...     ['res.partner*'],
            ...     ['res.partner.title', 'res.partner.bank'],
            ...     restrict=True,
            ... ).write('dependencies_res_partner_base_restricted.png', format='png')

        In any case, root `modules` are always displayed on the graph in
        restricted mode (even if they have no matching model), and some
        unrelated modules may be added to satisfy dependencies.

        `config` is a dictionary of options to override some attributes of
        the graph. Here the list of options and their default values:

            - ``module_uninst_bgcolor_title: #DEDFDE``,
            - ``module_uninst_color_title: black``,
            - ``module_inst_bgcolor_title: #64629C``,
            - ``module_inst_color_title: white``,
            - ``module_root_bgcolor_title: #A50018``,
            - ``module_root_color_title: white``,
            - ``module_highlight_bgcolor_title: #1F931F``,
            - ``module_highlight_color_title: white``,
            - ``module_bgcolor: white``,
            - ``module_color_comment: grey``,
            - ``model_color_normal: black``,
            - ``model_color_transient: #7D7D7D``,
            - ``show_module_inst: True``,
            - ``show_module_uninst: False``,
            - ``show_model_normal: True``,
            - ``show_model_transient: False``,

        >>> oerp.inspect.dependencies(
        ...     ['base'],
        ...     ['res.partner*'],
        ...     ['res.partner.title', 'res.partner.bank'],
        ...     config={'show_model_transient': True},  # Show TransientModel/osv_memory models
        ... ).write('dependencies_res_partner_transient.png', format='png')

        .. note::
            With `OpenERP` `5.0`, data models can not be bound to their related
            modules, and as such the `models` and `models_blacklist`
            parameters are ignored.

    """
    def __init__(self, oerp):
        self._oerp = oerp

    def relations(self, models, maxdepth=1, whitelist=None, blacklist=None,
                  attrs_whitelist=None, attrs_blacklist=None, config=None):
        from oerplib.service.inspect.relations import Relations
        return Relations(
            self._oerp, models, maxdepth, whitelist, blacklist,
            attrs_whitelist, attrs_blacklist, config)

    def scan_on_change(self, models):
        """Scan all `on_change` methods detected among views of `models`, and
        returns a dictionary formatted as
        ``{model: {on_change: {view_id: field: [args]}}}``

            >>> oerp.inspect.scan_on_change(['sale.order'])
            {'sale.order': {
                'onchange_partner_id': {
                    'sale.view_order_form': {
                        'partner_id': ['partner_id']}},
                'onchange_partner_order_id': {
                    'sale.view_order_form': {
                        'partner_order_id': ['partner_order_id', 'partner_invoice_id', 'partner_shipping_id']}},
                'onchange_pricelist_id': {
                    'sale.view_order_form': {
                        'pricelist_id': ['pricelist_id', 'order_line']}},
                'onchange_shop_id': {
                    'sale.view_order_form': {
                        'shop_id': ['shop_id']}},
                'shipping_policy_change': {
                    'sale.view_order_form': {
                        'order_policy': ['order_policy']}}},
             'sale.order.line': {
                'product_id_change': {
                    'sale.view_order_form': {
                        'product_id': [
                            'parent.pricelist_id', 'product_id', 'product_uom_qty', 'product_uom',
                            'product_uos_qty', 'product_uos', 'name', 'parent.partner_id', False, True,
                            'parent.date_order', 'product_packaging', 'parent.fiscal_position', False, 'context'],
                        'product_uom_qty': [
                            'parent.pricelist_id', 'product_id', 'product_uom_qty', 'product_uom',
                            'product_uos_qty', 'product_uos', 'name', 'parent.partner_id', False, False,
                            'parent.date_order', 'product_packaging', 'parent.fiscal_position', True, 'context']}},
                ...
             }}
        """
        from oerplib.service.inspect.on_change import scan_on_change
        return scan_on_change(self._oerp, models)

    def dependencies(self, modules=None, models=None, models_blacklist=None,
                     restrict=False, config=None):
        from oerplib.service.inspect.dependencies import Dependencies
        return Dependencies(
            self._oerp, modules, models, models_blacklist, restrict, config)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
