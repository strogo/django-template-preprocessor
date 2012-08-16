# -*- coding: utf-8 -*-

from unittest import TestCase

from test_project.helpers import compile_source


class TestSimpleTemplateInheritance(TestCase):
    
    def test_should_expand_one_level_inheritance(self):
        compiled = compile_source('{% extends "inheritance/level-one.html" %}').strip()
        self.assertEqual(compiled, 'BASE TEMPLATE')

    def test_should_expand_two_level_inheritance(self):
        compiled = compile_source('{% extends "inheritance/level-two.html" %}').strip()
        self.assertEqual(compiled, 'BASE TEMPLATE')

