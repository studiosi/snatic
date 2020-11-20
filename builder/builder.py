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

    # Get content file name
    @staticmethod
    def get_content_filename(filename):
        return os.path.join('data/content', filename)

    # Get template file name
    def get_template_filename(self, name):
        template_name = name + ".j2"
        theme = self.__config['theme']
        return os.path.join('themes/', theme, template_name)

    # Gets the output filename
    @staticmethod
    def get_output_filename(name, filetype):
        if filetype == BuilderOutputTypes.TYPE_HTML:
            filename = name + '.html'
            return os.path.join('site/html', filename)

    def build_page(self, page_cfg, is_home=False):
        content_filename = Builder.get_content_filename(page_cfg['file'])
        template_filename = self.get_template_filename('page')
        if is_home:
            output_filename = Builder.get_output_filename('index', BuilderOutputTypes.TYPE_HTML)
        else:
            output_filename = Builder.get_output_filename(page_cfg['slug'], BuilderOutputTypes.TYPE_HTML)
        with open(content_filename, 'r') as f_content, \
                open(template_filename, 'r') as f_template, \
                open(output_filename, 'w') as f_output:
            md_content = f_content.read()
            html_content = markdown(md_content)
            template_content = f_template.read()
            template = Template(template_content)
            f_output.write(template.render({
                'title': self.__config['home']['title'],
                'content': html_content
            }))

    # Builds the site
    def build(self):
        # Check the configuration
        self.check_config()
        # If site directory exists delete its contents
        if os.path.exists('site/'):
            print("Deleting the current site... ", end="")
            rmtree('site/')
            print("FINISHED")
        os.mkdir('site/')
        os.mkdir('site/html')
        # Install PHP dependencies on site folder
        Builder.install_php_dependencies()
        # Build HOME
        # Read content from MD file as comes in the config
        route_data = []
        print("Building pages...", end="")
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
        print("FINISHED")
        print("Building app...", end="")
        # Generate routes for static pages
        routes_content = ""
        with open('builder/templates/route.j2', "r") as f_template:
            template_content = f_template.read()
            route_template = Template(template_content)
            for route in route_data:
                routes_content += route_template.render(route)
        # Generating F3 Application
        with open('builder/templates/application.j2', "r") as f_application, \
                open('site/index.php', "w") as f_output:
            template_content = f_application.read()
            application_template = Template(template_content)
            application_code = application_template.render({
                'routes': routes_content
            })
            f_output.write(application_code)
        print("FINISHED")
        # Generating .htaccess
        print("Writing htaccess... ", end="")
        with open('builder/templates/htaccess.j2', "r") as f_application, \
                open('site/.htaccess', "w") as f_output:
            htaccess_content = f_application.read()
            htaccess_template = Template(htaccess_content)
            htaccess_code = htaccess_template.render()
            f_output.write(htaccess_code)
        print("FINISHED")
        # Copying assets from data to site
        print("Copying assets... ", end="")
        if os.path.exists('data/assets'):
            copytree('data/assets', 'site/assets')
        print("FINISHED")

    # Install PHP dependencies into the site
    @staticmethod
    def install_php_dependencies():
        print("Installing PHP dependencies... ", end="")
        os.chdir('site/')
        Executor.execute_command(['composer', 'require', 'bcosca/fatfree'])
        os.chdir('..')
        print("FINISHED")
