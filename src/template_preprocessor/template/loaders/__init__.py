# Author: Jonathan Slenders, City Live

# Template loaders

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader, get_template_from_string, find_template_loader, make_origin
from django.utils import translation
from django.utils.hashcompat import sha_constructor
from django.utils.importlib import import_module
from django.template import StringOrigin

from template_preprocessor.core import compile

import os
import codecs


class _Base(BaseLoader):
    is_usable = True

    def __init__(self, loaders):
        self._loaders = loaders

    @property
    def loaders(self):
        # Resolve loaders on demand to avoid circular imports
        if not self._cached_loaders:
            for loader in self._loaders:
                self._cached_loaders.append(find_template_loader(loader))
        return self._cached_loaders

    def find_template(self, name, dirs=None):
        for loader in self.loaders:
            try:
                template, display_name = loader.load_template_source(name, dirs)
                return (template, make_origin(display_name, loader.load_template_source, name, dirs))
            except TemplateDoesNotExist, e:
                pass
            except NotImplementedError, e:
                raise Exception('Template loader %s does not implement load_template_source. Be sure not to nest '
                            'loaders which return only Template objects into the template preprocessor. (We need '
                            'a loader which returns a template string.)' % unicode(loader))
        raise TemplateDoesNotExist(name)


class PreprocessedLoader(_Base):
    """
    Use preprocessed templates.
    If no precompiled version is available, use the original version, but don't compile at runtime.
    """
    __cache_dir = settings.TEMPLATE_CACHE_DIR

    def __init__(self, loaders):
        _Base.__init__(self, loaders)

        self.template_cache = {}
        self._cached_loaders = []

    def load_template(self, template_name, template_dirs=None):
        lang = translation.get_language() or 'en'
        key = '%s-%s' % (lang, template_name)

        if key not in self.template_cache:
            # Path in the cache directory
            output_path = os.path.join(self.__cache_dir, lang, template_name)

            # Load template
            if os.path.exists(output_path):
                # Prefer precompiled version
                template = codecs.open(output_path, 'r', 'utf-8').read()
                origin = StringOrigin(template)
            else:
                template, origin = self.find_template(template_name, template_dirs)

                # Compile template (we shouldn't compile anything at runtime.)
                #template = compile(template, loader = lambda path: self.find_template(path)[0], path=template_name)

            # Turn into Template object
            template = get_template_from_string(template, origin, template_name)

            # Save in cache
            self.template_cache[key] = template

        # Return result
        return self.template_cache[key], None


    def reset(self):
        "Empty the template cache."
        self.template_cache.clear()


class RuntimeProcessedLoader(_Base):
    """
    Load templates through the preprocessor. Compile at runtime.
    """
    def __init__(self, loaders):
        _Base.__init__(self, loaders)
        self._cached_loaders = []

    def load_template(self, template_name, template_dirs=None):
        template, origin = self.find_template(template_name, template_dirs)

        # Compile template (we shouldn't compile anything at runtime.)
        template = compile(template, loader = lambda path: self.find_template(path)[0], path=template_name)

        # Turn into Template object
        template = get_template_from_string(template, origin, template_name)

        # Return result
        return template, None

    def reset(self):
        "Empty the template cache."
        self.template_cache.clear()


class ValidatorLoader(_Base):
    """
    Wrapper for validating templates through the preprocessor. For Django 1.2
    It will compile the templates as a test and possibly raises CompileException
    when it fails to. But it still returns a Template object of the original
    template, without any caching.
    """
    def __init__(self, loaders):
        _Base.__init__(self, loaders)
        self._cached_loaders = []

    def load_template(self, template_name, template_dirs=None):
        # IMPORTANT NOTE:  We load the template, using the original loaders.
        #                  call compile, but still return the original,
        #                  unmodified result.  This causes the django tocall
        #                  load_template again for every include node where of
        #                  course the validation may fail. (incomplete HTML
        #                  tree, maybe only javascript, etc...)

        # Load template
        template, origin = self.find_template(template_name, template_dirs)

        # Compile template as a test (could raise CompileException), throw away the compiled result.
        try:
            # Don't compile template when a parent frame was a 'render' method. Than it's probably a
            # runtime call from an IncludeNode or ExtendsNode.
            import inspect
            if not any(map(lambda i:'render' == i[3], inspect.getouterframes(inspect.currentframe()))):
                #print 'compiling %s' % template_name
                compile(template, loader = lambda path: self.find_template(path)[0], path=template_name)
        except Exception, e:
            print '---'
            print 'Template: %s' % template_name
            print e
            print '-'
            import traceback
            traceback.print_exc()
            print '---'
            raise e

        # Turn into Template object
        template = get_template_from_string(template, origin, template_name)

        # Return template
        return template, None