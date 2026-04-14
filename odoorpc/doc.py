# Copyright 2026 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
"""Module to fetch data model informations from Odoo."""

from odoorpc.rpc import HTTPError


class ModelDoc:
    """Cache for model information from Odoo's /doc-bearer endpoint.

    This class fetches model metadata from `/doc-bearer/<model>.json`.

    It allows to guess if a method is @api.model decorated, or to translate
    positional arguments into named ones (starting from Odoo 19.0, the JSON-2
    API forbid positional arguments).

    :param odoo: the :class:`odoorpc.odoo.ODOO` instance
    """

    def __init__(self, odoo):
        self._odoo = odoo
        self._cache = {}

    def has_model(self, model_name):
        """Check if a model has been fetched.

        :param model_name: the name of the model
        :return: True if the model is in the cache
        """
        return model_name in self._cache

    def fetch(self, model_name):
        """Fetch method parameter information for a model from the
        `/doc-bearer/<model_name>.json` endpoint.

        :param model_name: the name of the model (e.g., 'res.partner')
        """
        if self.has_model(model_name):
            return
        try:
            self._cache[model_name] = self._odoo.json(
                "/doc-bearer/%s.json" % model_name
            )
        except HTTPError:
            return

    def get_method_info(self, model_name, method_name):
        """Return method informations, or None if the model or method is not cached.

        :param model_name: the name of the model
        :param method_name: the name of the method
        :return: list of parameter names or None
        """
        if self._cache.get(model_name, {}).get("methods", {}).get(method_name):
            return self._cache[model_name]["methods"][method_name]

    def transform_method_args_to_kwargs(self, model_name, method_name, args):
        """Transform `args` parameters of a method to `kwargs` for JSON-2 compatibility.

        :param model_name: the name of the model
        :param method_name: the name of the method
        :param args: the list of positional parameters
        :return: dict of named parameters
        """
        self.fetch(model_name)
        info = self.get_method_info(model_name, method_name)
        if not info:
            return {}
        params = list(info["parameters"].keys())
        kwargs = {}
        # Handle IDs on instance method
        if "model" not in info.get("api", []):
            # Instance method => first argument is record IDs
            kwargs["ids"] = args[0]
            args = args[1:]
        # Handle remaining parameters
        if params:
            for i, arg in enumerate(args):
                if i < len(params):
                    kwargs[params[i]] = arg
        return kwargs
