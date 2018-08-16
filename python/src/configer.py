"""
This file aims to load configurations from both setting.ini and
put them into a static class named Configer

Attributes:
    logger (TYPE): Description

"""
import sys
import logging

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser as ConfigParser


logger = logging.getLogger(__name__)


class Singleton(type):

    """Summary
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Summary

        Args:
            *args: Description
            **kwargs: Description

        Returns:
            TYPE: Description
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Configer(object):
    """
    This class will load all parameters from setting.ini


    """
    __metaclass__ = Singleton

    def __init__(self, setting_file_path):
        """
        Init Configer class and load all settings from file

        Args:
            setting_file_path (str): full path to setting file
        """
        logger.info('init Configer object, setting file = %s',
                    setting_file_path)
        self.setting_file_path = setting_file_path

        section_name = 'SectionServer'
        self.ip_address = self.load_configuration(section_name, 'IPAddress')
        self.port = int(self.load_configuration(section_name, 'Port'))
        self.ssh_username = self.load_configuration(
            section_name, 'SshUsername')
        self.ssh_password = self.load_configuration(
            section_name, 'SshPassword')
        self.use_ssh = True if self.load_configuration(
            section_name, 'UseSSH') == 1 else False

        section_name = 'SectionDatabase'
        self.db_name = self.load_configuration(section_name, 'DatabaseName')
        self.db_username = self.load_configuration(
            section_name, 'DatabaseUsername')
        self.db_password = self.load_configuration(
            section_name, 'DatabasePassword')
        self.search_path = self.load_configuration(section_name, 'SearchPath')

    def load_configuration(self, section, config_name):
        """
        Description: load configuration from setting file using ConfigParser

        Args:
            section (str): name of section in setting file
            config_name (str): name of configuration

        Returns:
            STR: value of configuration

        Raises:
            IOError: Description

        """

        config = ConfigParser.ConfigParser()
        if not config.read(self.setting_file_path):
            raise IOError('cannot load ' + self.setting_file_path)

        return config.get(section, config_name)

temp = Configer('setting.ini')
