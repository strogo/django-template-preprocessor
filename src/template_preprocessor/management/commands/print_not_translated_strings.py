"""
Author: Jonathan Slenders, City Live
"""
import codecs
import os
import string
from optparse import make_option
import termcolor

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist

from template_preprocessor.core import compile_to_parse_tree
from template_preprocessor.core.lexer import CompileException

from template_preprocessor.utils import language, template_iterator, load_template_source, get_template_path
from template_preprocessor.utils import get_options_for_path, execute_precompile_command
from template_preprocessor.core.utils import need_to_be_recompiled, create_media_output_path
from template_preprocessor.core.context import Context


class Command(BaseCommand):
    help = "Preprocess all the templates form all known applications."
    option_list = BaseCommand.option_list + (
        make_option('--single-template', action='append', dest='single_template', help='Compile only this template'),
        make_option('--boring', action='store_true', dest='boring', help='No colors in output'),
    )

    def print_error(self, text):
        self._errors.append(text)
        print self.colored(text, 'white', 'on_red').encode('utf-8')


    def colored(self, text, *args, **kwargs):
        if self.boring:
            return text
        else:
            return termcolor.colored(text, *args, **kwargs)


    def handle(self, *args, **options):
        single_template = options['single_template']

        # Default verbosity
        self.verbosity = int(options.get('verbosity', 1))

        # Colors?
        self.boring = bool(options.get('boring'))

        self._errors = []

        # Build compile queue
        queue = self._build_compile_queue(single_template)

        # Compile queue
        for i in range(0, len(queue)):
                if self.verbosity >= 2:
                    print self.colored('%i / %i |' % (i+1, len(queue)), 'yellow'),
                    print self.colored(queue[i][1], 'green')

                self._compile_template(*queue[i])

        # Ring bell :)
        print '\x07'

    def _build_compile_queue(self, single_template=None):
        """
        Build a list of all the templates to be compiled.
        """
        # Create compile queue
        queue = set() # Use a set, avoid duplication of records.

        if self.verbosity >= 2:
            print 'Building queue'

        # Now compile all templates to the cache directory
        for dir, t in template_iterator():
            input_path = os.path.normpath(os.path.join(dir, t))

            # Compile this template if:
            if (
                    # We are compiling *everything*
                    not single_template or

                    # Or this is the only template that we want to compile
                    (single_template and t in single_template)):

                queue.add( (t, input_path) )

        # Return ordered queue
        queue = list(queue)
        queue.sort()
        return queue


    def _compile_template(self, template, input_path):
        try:
            try:
                # Open input file
                code = codecs.open(input_path, 'r', 'utf-8').read()
            except UnicodeDecodeError, e:
                raise CompileException(0, 0, input_path, str(e))
            except IOError, e:
                raise CompileException(0, 0, input_path, str(e))

            # Get options for this template
            options=get_options_for_path(input_path)
            options.append('no-i18n-preprocessing')

            # Compile
            tree, context = compile_to_parse_tree(code, path=input_path, loader=load_template_source,
                        options=options)

            # Now find all nodes, which contain text, but not in trans blocks.
            from template_preprocessor.core.html_processor import HtmlContent, HtmlStyleNode, HtmlScriptNode

            def contains_alpha(s):
                # Return True when string contains at least a letter.
                for i in s:
                    if i in string.ascii_letters:
                        return True
                return False

            for node in tree.child_nodes_of_class(HtmlContent, dont_enter=(HtmlStyleNode, HtmlScriptNode)):
                content = node.output_as_string()

                s = content.strip()
                if s and contains_alpha(s):
                    print self.colored(node.path, 'yellow'), '  ',
                    print self.colored(' %s:%s' % (node.line, node.column), 'red')
                    print s.encode('utf-8')

        except CompileException, e:
                # Print the error
                self.print_error(u'ERROR:  %s' % unicode(e))

        except TemplateDoesNotExist, e:
            if self.verbosity >= 2:
                print u'WARNING: Template does not exist:  %s' % unicode(e)
