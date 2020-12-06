import os
from enum import Enum
from jinja2 import Template
from setup.executor import Executor


class BuilderOutputTypes(Enum):
    TYPE_NONE = 0
    TYPE_HTML = 1
    TYPE_TEMPLATE = 2


class BuilderUtils:

    @staticmethod
    def get_content_filename(filename):
        return os.path.join('data/content', filename)

    @staticmethod
    def get_output_filename(name, filetype):
        if filetype == BuilderOutputTypes.TYPE_HTML:
            return os.path.join('site/html', name)

    @staticmethod
    def template_render(template_filename, data=None):
        with open(template_filename, 'r') as f:
            template_content = f.read()
            template_renderer = Template(template_content)
            if data is not None:
                return template_renderer.render(data)
            else:
                return template_renderer.render()

    @staticmethod
    def install_php_dependencies():
        print('Installing PHP dependencies... ', end='')
        os.chdir('site/')
        Executor.execute_command(['composer', 'require', 'bcosca/fatfree'])
        os.chdir('..')
        print('FINISHED')
