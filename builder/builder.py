import os

from enum import Enum
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from markdown import markdown
from jinja2 import Template, Environment, FileSystemLoader
from setup.executor import Executor
from shutil import rmtree, copytree
from datetime import datetime

from .configuration_exception import ConfigurationException
from .menu import Menu


class BuilderOutputTypes(Enum):
    TYPE_NONE = 0
    TYPE_HTML = 1
    TYPE_TEMPLATE = 2


class Builder:

    def __init__(self):
        self.__config = None
        self.__theme_template_env = None
        self.__internal_template_env = None
        self.read_config()
        self.create_template_environments()
        self.__menu = Menu(self.__config)

    # Creates the templating environment so templates can be composed
    def create_template_environments(self):
        self.__theme_template_env = Environment(
            loader=FileSystemLoader(os.path.join('themes/', self.__config['site_config']['theme']))
        )
        self.__internal_template_env = Environment(
            loader=FileSystemLoader('builder/templates')
        )

    # Reads the configuration file
    def read_config(self):
        with open('data/site.yaml', 'r') as config_file:
            self.__config = load(config_file.read(), Loader=Loader)

    # Checks that the configuration is OK
    def check_config(self):
        if 'name' not in self.__config['site_config'].keys():
            raise ConfigurationException('Name not defined in configuration')
        if 'home' not in self.__config['pages'].keys():
            raise ConfigurationException('Home not defined in configuration')
        if 'site_config' not in self.__config.keys():
            raise ConfigurationException('Site configuration not defined')
        if 'theme' not in self.__config['site_config'].keys():
            raise ConfigurationException('Theme not defined in site configuration')
        if not os.path.exists(os.path.join('themes/', self.__config['site_config']['theme'])):
            raise ConfigurationException(f'Theme {self.__config["site_config"]["theme"]} not found')

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

    # Gets the output filename
    @staticmethod
    def get_output_filename(name, filetype):
        if filetype == BuilderOutputTypes.TYPE_HTML:
            return os.path.join('site/html', name)

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
    def build_page(self, page_cfg):
        content_filename = Builder.get_content_filename(page_cfg['file'])
        template = self.__theme_template_env.get_template('page.j2')
        output_filename = Builder.get_output_filename(page_cfg['filename'], BuilderOutputTypes.TYPE_HTML)
        page_title = page_cfg['title']
        with open(content_filename, 'r') as f_content, \
                open(output_filename, 'w') as f_output:
            md_content = f_content.read()
            html_content = markdown(md_content)
            f_output.write(template.render({
                'name': self.__config['site_config']['name'],
                'title': page_title,
                'content': html_content,
                'menu': self.__menu.get_menu(),
                'creation_date': page_cfg['creation_date'],
                'build_date': datetime.now().strftime(self.__config['site_config']['dt_format'])
            }))

    # Builds a single archive page
    def build_archive(self, archive_cfg):
        pass

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
        print('Building pages... ', end='')
        # Build pages
        route_data = []
        for k in self.__config['pages'].keys():
            cfg = self.__config['pages'][k]
            if k.lower() == 'home':
                cfg['slug'] = ''
                cfg['filename'] = 'index.html'
            else:
                cfg['slug'] = self.__config["pages"][k]["slug"]
                cfg['filename'] = f'{self.__config["pages"][k]["slug"]}.html'
            built = False
            if self.__config['pages'][k]['type'].lower() == 'page':
                self.build_page(cfg)
                built = True
            elif self.__config['pages'][k]['type'].lower() == 'archive':
                self.build_archive(cfg)
                built = True
            if built:
                route_data.append({
                    'slug': cfg['slug'],
                    'filename': cfg['filename'],
                })
        print('FINISHED')
        print('Building app...', end='')
        # Generate routes for static pages
        routes_content = ''
        route_template = self.__internal_template_env.get_template('route.j2')
        for route in route_data:
            routes_content += route_template.render(route)
        # Generating F3 Application
        with open('site/index.php', 'w') as f_output:
            app_template = self.__internal_template_env.get_template('application.j2')
            f_output.write(app_template.render({'routes': routes_content}))
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
