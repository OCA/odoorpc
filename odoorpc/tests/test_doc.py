from odoorpc.doc import ModelDoc
from odoorpc.tests import LoginTestCase


class TestModelDoc(LoginTestCase):
    def setUp(self):
        LoginTestCase.setUp(self)
        self._skip_if_not_json2()

    def _skip_if_not_json2(self):
        if not self.odoo.json2_ready:
            self.skipTest("JSON-2 not ready (requires API key login on Odoo >= 19.0)")

    def test_doc_created_on_login(self):
        self.assertIsInstance(self.odoo._doc, ModelDoc)

    def test_doc_fetch(self):
        doc = self.odoo._doc
        doc.fetch("res.partner")
        self.assertTrue(doc.has_model("res.partner"))

    def test_doc_get_method_info(self):
        doc = self.odoo._doc
        doc.fetch("res.partner")
        info = doc.get_method_info("res.partner", "search")
        self.assertIsInstance(info, dict)
        self.assertIn("parameters", info)
        self.assertIn("domain", info["parameters"])

    def test_doc_get_method_info_unknown_model(self):
        doc = self.odoo._doc
        doc.fetch("res.partner")
        self.assertIsNone(doc.get_method_info("unknown.model", "search"))
        self.assertIsNone(doc.get_method_info("res.partner", "unknown_method"))

    def test_call_method_from__model(self):
        partner_ids = self.odoo.env["res.partner"].search([], limit=1)
        self.assertLessEqual(len(partner_ids), 1)
        if partner_ids:
            # Call with args
            data = self.odoo.env["res.partner"].read(partner_ids, ["name"])
            self.assertIsInstance(data, list)
            self.assertIn("name", data[0])
            # Call with kwargs
            data = self.odoo.env["res.partner"].read(partner_ids, fields=["name"])
            self.assertIsInstance(data, list)
            self.assertIn("name", data[0])

    def test_call_method_from_recordset(self):
        partner = self.odoo.env["res.partner"].browse([1])
        if partner:
            # Call with args
            data = partner.read(["name"])
            self.assertIsInstance(data, list)
            self.assertIn("name", data[0])
            # Call with kwargs
            data = partner.read(fields=["name"])
            self.assertIsInstance(data, list)
            self.assertIn("name", data[0])
