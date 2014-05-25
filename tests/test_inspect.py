# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except:
    import unittest

from args import ARGS

import oerplib


class TestInspect(unittest.TestCase):

    def setUp(self):
        self.oerp = oerplib.OERP(
            ARGS.server, protocol=ARGS.protocol, port=ARGS.port,
            version=ARGS.version)
        self.user = self.oerp.login(ARGS.user, ARGS.passwd, ARGS.database)

    def test_relations(self):
        graph = self.oerp.inspect.relations(
            ['res.users'],
            maxdepth=1,
            whitelist=['*'], blacklist=[],
            attrs_whitelist=['*'], attrs_blacklist=[])
        self.assertIsInstance(graph, oerplib.service.inspect.relations.Relations)

    def test_relations_maxdepth_null(self):
        graph = self.oerp.inspect.relations(['res.users'], maxdepth=0)
        self.assertIsInstance(graph, oerplib.service.inspect.relations.Relations)

    def test_relations_maxdepth_negative(self):
        graph = self.oerp.inspect.relations(['res.users'], maxdepth=-1)
        self.assertIsInstance(graph, oerplib.service.inspect.relations.Relations)

    def test_dependencies(self):
        graph = self.oerp.inspect.dependencies()
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_dependencies_with_module(self):
        graph = self.oerp.inspect.dependencies(['base'])
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_dependencies_with_models(self):
        graph = self.oerp.inspect.dependencies(models=['res.partner*'])
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_dependencies_with_wrong_module(self):
        self.assertRaises(
            oerplib.error.InternalError,
            self.oerp.inspect.dependencies, ['wrong_module'])

    def test_dependencies_with_module_and_models(self):
        graph = self.oerp.inspect.dependencies(['base'], ['res.partner*'])
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_dependencies_with_module_and_models_restricted(self):
        graph = self.oerp.inspect.dependencies(
            ['base'], ['res.partner*'], restrict=True)
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_dependencies_with_module_and_models_blacklist(self):
        graph = self.oerp.inspect.dependencies(
            ['base'], ['res.partner*'], ['res.partner.bank'])
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_dependencies_with_module_and_models_blacklist_restricted(self):
        graph = self.oerp.inspect.dependencies(
            ['base'], ['res.partner*'], ['res.partner.bank'], restrict=True)
        self.assertIsInstance(
            graph, oerplib.service.inspect.dependencies.Dependencies)

    def test_scan_on_change(self):
        res = self.oerp.inspect.scan_on_change(['res.users'])
        self.assertIsInstance(res, dict)
        res = self.oerp.inspect.scan_on_change(['res.users', 'res.partner'])
        self.assertIsInstance(res, dict)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
