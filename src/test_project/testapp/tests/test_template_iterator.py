
import os
from django.utils.unittest import TestCase
from django.conf import settings
from template_preprocessor.utils import template_iterator


class TemplateIteratorTestCase(TestCase):

    def setUp(self):
        self.template_paths = {}
        self.app_template_dir = os.path.join(settings.PROJECT_DIR, 'testapp')
        for dir, template_path in template_iterator():
            if template_path not in self.template_paths:
                self.template_paths[template_path] = [dir]
            else:
                self.template_paths[template_path].append(template_path)
        self.app_template_name = 'app-template.html'
        self.project_template_name = 'project-template.html'

    def test_prefer_templatedirs_than_app_templates(self):
        self.assertListEqual([settings.TEMPLATE_DIRS[0]],
                             self.template_paths[self.project_template_name])

    def test_use_the_app_order_returning_the_first_template_app(self):
        self.assertListEqual([os.path.join(self.app_template_dir, 'templates')],
                             self.template_paths[self.app_template_name])

    def test_must_return_one_entry_from_both_project_and_app_which_have_the_same_template(self):
        self.assertEqual(1,
                         len(self.template_paths[self.project_template_name]))

    def test_must_return_one_entry_when_two_apps_have_the_same_template(self):
        self.assertEqual(1,
                         len(self.template_paths[self.app_template_name]))
