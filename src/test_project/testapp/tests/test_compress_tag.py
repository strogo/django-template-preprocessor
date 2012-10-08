# -*- coding: utf-8 -*-

from unittest import TestCase

from test_project.helpers import compile_source

class TestTemplateInclude(TestCase):

    def test_should_strip_compress_tag(self):
        compiled = compile_source('{% compress js %}<script src="{{ STATIC_URL }}js1.js"></script><script src="{{ STATIC_URL }}js2.js"></script>{% endcompress %}').strip()
        self.assertEqual(compiled, '<script src="/static/js1.js"></script><script src="/static/js2.js"></script>')

    def test_should_strip_compress_tag_and_pack_scripts(self):
        options = ('pack-external-javascript',)
        compiled = compile_source('{% compress js %}<script src="{{ STATIC_URL }}js1.js"></script><script src="{{ STATIC_URL }}js2.js"></script>{% endcompress %}', options=options).strip()
        self.assertEqual(compiled, '<script src="/media/cache/en-us/8c4e8312d3db60c305e5361780ce06ad.js"></script>')

    def test_should_keep_compress_tag_unless_html(self):
        options=('no-html',)
        compiled = compile_source('{% compress js %}<script src="{{ STATIC_URL }}js1.js"></script><script src="{{ STATIC_URL }}js2.js"></script>{% endcompress %}', options=options).strip()
        self.assertEqual(compiled, '{%compress js %}<script src="/static/js1.js"></script><script src="/static/js2.js"></script>{%endcompress %}')
