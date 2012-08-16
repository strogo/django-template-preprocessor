# -*- coding: utf-8 -*-

from unittest import TestCase

from test_project.helpers import compile_source


class TestSimpleTemplateInheritance(TestCase):
    
    def test_should_expand_one_level_inheritance(self):
        compiled = compile_source('{% extends "inheritance/base.html" %}').strip()
        self.assertEqual(compiled, 'BASE TEMPLATE')

    def test_should_expand_two_level_inheritance(self):
        compiled = compile_source('{% extends "inheritance/level-one.html" %}').strip()
        self.assertEqual(compiled, 'BASE TEMPLATE')

    def test_should_expand_app_template_inheriting_from_template_dirs(self):
        compiled = compile_source('{% extends "inheritance/inherit-from-template-dirs.html" %}').strip()
        self.assertEqual(compiled, 'BASE TEMPLATE')


class TestSimpleTemplateInheritanceWithBlocks(TestCase):
    
    def test_should_expand_block_from_base_template(self):
        template = '{% extends "blocks/base.html" %}'
        compiled = compile_source(template).strip()
        self.assertEqual(compiled, 'BASE BLOCK')

    def test_should_keep_overriden_block(self):
        template = '{% extends "blocks/base.html" %}{% block base_block %}OVERRIDEN{% endblock %}'
        compiled = compile_source(template).strip()
        self.assertEqual(compiled, 'OVERRIDEN')

    def test_should_keep_overriden_block_plus_super(self):
        template = '''
            {% extends "blocks/base.html" %}
            {% block base_block %}{{ block.super }} + OVERRIDEN{% endblock %}
        '''
        compiled = compile_source(template).strip()
        self.assertEqual(compiled, 'BASE BLOCK + OVERRIDEN')

