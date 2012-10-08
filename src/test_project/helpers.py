# -*- coding: utf-8 -*-

from django.conf import settings

from template_preprocessor.core import compile
from template_preprocessor.template.loaders import _Base as BaseLoader
from template_preprocessor.core.context import Context


class HelperLoader(BaseLoader):

    options = ()
    context_class = Context

    def __init__(self, loaders=settings.TEMPLATE_LOADERS):
        super(HelperLoader, self).__init__(loaders=loaders)

    def compile_template(self, original_source, template_dirs=None, options=None):
        template_source, context = compile(
            original_source,
            loader = lambda path: self.find_template(path)[0],
            options=options or self.options,
            context_class=self.context_class
        )

        return template_source


def compile_source(source, options=None):
    return HelperLoader().compile_template(source, options=options)
