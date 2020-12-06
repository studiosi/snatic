import os

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from jinja2 import Environment, FileSystemLoader
from shutil import rmtree, copytree

from .menu import Menu

from .type_builders import *
from .builder_utils import BuilderUtils
from .config_utils import ConfigUtils


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

    # Builds the site
    def build(self):
        # Check the configuration
        ConfigUtils.check_config(self.__config)
        # If site directory exists delete its contents
        if os.path.exists('site/'):
            print('Deleting the current site... ', end='')
            rmtree('site/')
            print('FINISHED')
        os.mkdir('site/')
        os.mkdir('site/html')
        # Install PHP dependencies on site folder
        BuilderUtils.install_php_dependencies()
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
                PageBuilder.build(self.__config, cfg, self.__menu, self.__theme_template_env)
                built = True
            elif self.__config['pages'][k]['type'].lower() == 'archive':
                ArchiveBuilder.build(self.__config, cfg, self.__config['pages'], self.__menu, self.__theme_template_env)
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
            f_output.write(BuilderUtils.template_render('builder/templates/htaccess.j2'))
        print('FINISHED')
        # Copying assets from data to site
        print('Copying assets... ', end='')
        if os.path.exists('data/assets'):
            copytree('data/assets', 'site/assets')
        print('FINISHED')
