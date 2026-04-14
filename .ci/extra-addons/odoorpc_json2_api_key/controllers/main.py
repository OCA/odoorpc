# Copyright 2026 Sébastien Alix
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, http


class TestHttp(http.Controller):
    @http.route("/generate_test_api_key", type="http", auth="public")
    def generate_test_api_key(self):
        """Test endpoint to generate an API key used by OdooRPC.

        /!\ This is a security breach open only for testing purpose /!\
        """
        user_model = http.request.env["res.users"].sudo()
        admin = user_model.env.ref("base.user_admin")
        admin = admin.with_user(admin)
        now = fields.Datetime.now()
        expiration_date = fields.Datetime.add(now, days=0.5)
        return admin.env["res.users.apikeys"]._generate(
            scope="rpc",
            name="test",
            expiration_date=expiration_date,
        )
