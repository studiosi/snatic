import os
from .configuration_exception import ConfigurationException


class ConfigUtils:

    @staticmethod
    def check_config(cfg):
        if 'name' not in cfg['site_config'].keys():
            raise ConfigurationException('Name not defined in configuration')
        if 'home' not in cfg['pages'].keys():
            raise ConfigurationException('Home not defined in configuration')
        if 'site_config' not in cfg.keys():
            raise ConfigurationException('Site configuration not defined')
        if 'theme' not in cfg['site_config'].keys():
            raise ConfigurationException('Theme not defined in site configuration')
        if not os.path.exists(os.path.join('themes/', cfg['site_config']['theme'])):
            raise ConfigurationException(f'Theme {cfg["site_config"]["theme"]} not found')
