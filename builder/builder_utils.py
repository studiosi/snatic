import os
from enum import Enum
from jinja2 import Template
from setup.executor import Executor
from shutil import rmtree, copytree


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

    @staticmethod
    def delete_current_site():
        if os.path.exists('site/'):
            print('Deleting the current site... ', end='')
            rmtree('site/')
            print('FINISHED')
        os.mkdir('site/')
        os.mkdir('site/html')

    @staticmethod
    def create_htaccess():
        print('Writing htaccess... ', end='')
        with open('site/.htaccess', 'w') as f_output:
            f_output.write(BuilderUtils.template_render('builder/templates/htaccess.j2'))
        print('FINISHED')

    @staticmethod
    def copy_assets():
        print('Copying assets... ', end='')
        if os.path.exists('data/assets'):
            copytree('data/assets', 'site/assets')
        print('FINISHED')

    @staticmethod
    def copy_theme_assets(theme):
        print('Copying theme assets... ', end='')
        theme_assets_path = os.path.join('themes/', theme + '/', 'theme-assets')
        if os.path.exists(theme_assets_path):
            copytree(theme_assets_path, 'site/theme-assets')
        print('FINISHED')
