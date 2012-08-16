# -*- coding: utf-8 -*-

from unittest import TestCase
from template_preprocessor.core.lexer import CompileException

from test_project.helpers import compile_source

class TestTemplateInclude(TestCase):

    def test_should_include_template_markup(self):
        compiled = compile_source('{% include "include/include_template.html" %}').strip()
        self.assertEqual(compiled, 'include template')

    def test_include_a_dynamic_variable_should_not_include_template_markup(self):
        compiled = compile_source('{% include dynamic_template %}').strip()
        self.assertEqual(compiled, '{%include dynamic_template%}')

    def test_should_raise_a_compileException_when_template_doesnt_exists(self):
        self.assertRaises(CompileException, compile_source, '{% include "include/notfound_template.html" %}')
