# -*- coding: utf-8 -*-
import os
import time

import odoorpc

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from odoorpc.tools import v


class BaseTestCase(unittest.TestCase):
    """Instanciates an ``odoorpc.ODOO`` object and a test database."""

    @classmethod
    def setUpClass(cls):
        try:
            port = int(os.environ.get("ORPC_TEST_PORT", 8069))
        except (ValueError, TypeError):
            raise ValueError("The port must be an integer")
        cls.env = {
            "protocol": os.environ.get("ORPC_TEST_PROTOCOL", "jsonrpc"),
            "host": os.environ.get("ORPC_TEST_HOST", "localhost"),
            "port": port,
            "db": os.environ.get("ORPC_TEST_DB", "odoorpc_test"),
            "user": os.environ.get("ORPC_TEST_USER", "admin"),
            "pwd": os.environ.get("ORPC_TEST_PWD", "admin"),
            "version": os.environ.get("ORPC_TEST_VERSION", None),
            "super_pwd": os.environ.get("ORPC_TEST_SUPER_PWD", "admin"),
        }
        cls.odoo = odoorpc.ODOO(
            cls.env["host"],
            protocol=cls.env["protocol"],
            port=cls.env["port"],
            version=cls.env["version"],
        )
        # Create the database
        default_timeout = cls.odoo.config["timeout"]
        cls.odoo.config["timeout"] = 600
        if cls.env["db"] not in cls.odoo.db.list():
            cls.odoo.db.create(cls.env["super_pwd"], cls.env["db"], True)
        cls.odoo.config["timeout"] = default_timeout


class LoginTestCase(BaseTestCase):
    """Login on the test database and install some modules."""

    @classmethod
    def setUpClass(cls):
        BaseTestCase.setUpClass()
        default_timeout = cls.odoo.config["timeout"]
        try:
            cls.odoo._check_logged_user()
        except odoorpc.error.InternalError:
            if v(cls.odoo.version)[0] >= 19:
                # Odoo >= 19.0 supports JSON-2 connection which requires an API key.
                # NOTE: /generate_test_api_key endpoint is provided by
                # 'odoorpc_json2_api_key' module.
                resp = cls.odoo.http(
                    "/generate_test_api_key",
                    headers={"X-Odoo-Database": cls.env["db"]},
                )
                key = resp.read().decode()
                cls.odoo.login(cls.env["db"], api_key=key)
            else:
                cls.odoo.login(cls.env["db"], cls.env["user"], cls.env["pwd"])
        cls._disable_cron_jobs()
        # Install 'sale' + 'crm_claim' on Odoo < 10.0,
        # 'sale' + 'subscription' on Odoo == 10.0
        # and only 'sale' on > 10.0
        cls.odoo.config["timeout"] = 600
        module_obj = cls.odoo.env["ir.module.module"]
        modules = ["sale", "crm_claim"]
        if v(cls.odoo.version)[0] == 10:
            modules = ["sale", "subscription"]
        elif v(cls.odoo.version)[0] >= 11:
            modules = ["sale"]
        domain = [("name", "in", modules), ("state", "!=", "installed")]
        module_ids = cls._search("ir.module.module", domain)
        if module_ids:
            if cls.odoo.json2_ready:
                module_obj.button_immediate_install(ids=module_ids)
            else:
                module_obj.button_immediate_install(module_ids)
        cls.odoo.config["timeout"] = default_timeout
        # Get user record and model after the installation of modules
        # to get all available fields (avoiding test failures)
        cls.user = cls.odoo.env.user
        cls.user_obj = cls.odoo.env["res.users"]

    @classmethod
    def _disable_cron_jobs(cls):
        # Disable cron jobs so installation of modules in tests doesn't
        # trigger "Odoo is currently processing a scheduled action." error.
        cron_ids = cls._search("ir.cron", [])
        if not cron_ids:
            return
        cron_disabled = False
        attempts = 0
        while not cron_disabled and attempts < 20:
            try:
                cls._write("ir.cron", cron_ids, {"active": False})
            except odoorpc.error.RPCError:
                time.sleep(1)  # Let's wait a bit before trying again
                attempts += 1
            else:
                cron_disabled = True

    @classmethod
    def _install_lang(cls, lang_code):
        Wizard = cls.odoo.env["base.language.install"]
        if v(cls.odoo.version)[0] >= 16:
            lang_ids = cls._search(
                "res.lang", [("code", "=", lang_code)], active_test=False
            )
            wiz_values = {"lang_ids": [(6, 0, lang_ids)]}
        else:
            wiz_values = {"lang": "fr_FR"}
        wiz_id = cls._create("base.language.install", wiz_values)
        wiz = Wizard.browse(wiz_id)
        wiz.lang_install()

    @classmethod
    def _search(cls, model, domain, limit=None, **context):
        model = cls.odoo.env[model].with_context(**context)
        if cls.odoo.json2_ready:
            return model.search(domain=domain, limit=limit)
        return model.search(domain, limit=limit)

    @classmethod
    def _create(cls, model, vals_list, **context):
        model = cls.odoo.env[model].with_context(**context)
        if cls.odoo.json2_ready:
            ids = model.create(vals_list=vals_list)
        else:
            ids = model.create(vals_list)
        if isinstance(ids, list) and len(ids) == 1:
            return ids[0]
        return ids

    @classmethod
    def _read(cls, model, ids, fields=None, **context):
        model = cls.odoo.env[model].with_context(**context)
        if cls.odoo.json2_ready:
            return model.read(ids=ids, fields=fields)
        return model.read(ids, fields)

    @classmethod
    def _write(cls, model, ids, vals, **context):
        model = cls.odoo.env[model].with_context(**context)
        if cls.odoo.json2_ready:
            return model.write(ids=ids, vals=vals)
        return model.read(ids, vals)
