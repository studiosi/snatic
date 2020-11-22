import os
from enum import Enum
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from .configuration_exception import ConfigurationException
from markdown import markdown
from jinja2 import Template
from setup.executor import Executor
from shutil import rmtree, copytree


class BuilderOutputTypes(Enum):
    TYPE_NONE = 0
    TYPE_HTML = 1
    TYPE_TEMPLATE = 2


class Builder:

    def __init__(self):
        self.__config = None
        self.read_config()

    # Reads the configuration file
    def read_config(self):
        with open('data/site.yaml', 'r') as config_file:
            self.__config = load(config_file.read(), Loader=Loader)

    # Checks that the configuration is OK
    def check_config(self):
        if 'home' not in self.__config.keys():
            raise ConfigurationException('Home not defined in configuration')
        if 'theme' not in self.__config.keys():
            raise ConfigurationException('Theme not defined in configuration')
        if not os.path.exists(os.path.join('themes/', self.__config['theme'])):
            raise ConfigurationException(f'Theme {self.__config["theme"]} not found')

    # Install PHP dependencies into the site
    @staticmethod
    def install_php_dependencies():
        print('Installing PHP dependencies... ', end='')
        os.chdir('site/')
        Executor.execute_command(['composer', 'require', 'bcosca/fatfree'])
        os.chdir('..')
        print('FINISHED')

    # Get content file name
    @staticmethod
    def get_content_filename(filename):
        return os.path.join('data/content', filename)

    # Get template file name
    def get_template_filename(self, name):
        template_name = name + '.j2'
        theme = self.__config['theme']
        return os.path.join('themes/', theme, template_name)

    # Gets the output filename
    @staticmethod
    def get_output_filename(name, filetype):
        if filetype == BuilderOutputTypes.TYPE_HTML:
            filename = name + '.html'
            return os.path.join('site/html', filename)

    # Renders a template and returns the rendered contents
    @staticmethod
    def template_render(template_filename, data=None):
        with open(template_filename, 'r') as f:
            template_content = f.read()
            template_renderer = Template(template_content)
            if data is not None:
                return template_renderer.render(data)
            else:
                return template_renderer.render()

    # Builds a single page
    def build_page(self, page_cfg, is_home=False):
        content_filename = Builder.get_content_filename(page_cfg['file'])
        template_filename = self.get_template_filename('page')
        if is_home:
            output_filename = Builder.get_output_filename('index', BuilderOutputTypes.TYPE_HTML)
            page_title = self.__config['home']['title']
        else:
            output_filename = Builder.get_output_filename(page_cfg['slug'], BuilderOutputTypes.TYPE_HTML)
            page_title = page_cfg['title']
        with open(content_filename, 'r') as f_content, \
                open(output_filename, 'w') as f_output:
            md_content = f_content.read()
            html_content = markdown(md_content)
            f_output.write(Builder.template_render(template_filename, {
                'title': page_title,
                'content': html_content
            }))

    # Builds the site
    def build(self):
        # Check the configuration
        self.check_config()
        # If site directory exists delete its contents
        if os.path.exists('site/'):
            print('Deleting the current site... ', end='')
            rmtree('site/')
            print('FINISHED')
        os.mkdir('site/')
        os.mkdir('site/html')
        # Install PHP dependencies on site folder
        Builder.install_php_dependencies()
        # Build HOME
        # Read content from MD file as comes in the config
        route_data = []
        print('Building pages... ', end='')
        self.build_page(self.__config['home'], is_home=True)
        route_data.append({
            'slug': '',
            'filename': 'index.html'
        })
        # Build the rest of the pages
        for k in self.__config['pages'].keys():
            self.build_page(self.__config['pages'][k])
            route_data.append({
                'slug': self.__config['pages'][k]['slug'],
                'filename': f'{ self.__config["pages"][k]["slug"] }.html'
            })
        print('FINISHED')
        print('Building app...', end='')
        # Generate routes for static pages
        routes_content = ''
        for route in route_data:
            routes_content += Builder.template_render('builder/templates/route.j2', route)
        # Generating F3 Application
        with open('site/index.php', 'w') as f_output:
            f_output.write(Builder.template_render(
                'builder/templates/application.j2',
                {
                    'routes': routes_content
                }
            ))
        print('FINISHED')
        # Generating .htaccess
        print('Writing htaccess... ', end='')
        with open('site/.htaccess', 'w') as f_output:
            f_output.write(Builder.template_render('builder/templates/htaccess.j2'))
        print('FINISHED')
        # Copying assets from data to site
        print('Copying assets... ', end='')
        if os.path.exists('data/assets'):
            copytree('data/assets', 'site/assets')
        print('FINISHED')
