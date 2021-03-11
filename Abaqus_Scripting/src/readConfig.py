import configparser


class ReadConfig:
    file_name = None
    abaqus_file_path = None

    def __init__(self):
        try:
            self.read_config()

        except IOError:
            self.create_config()

    def read_config(self):
        """Reading Config
        ==================

        If there is a config file, than it reads its content

        Reading:
        1. File Name
        2. File Path

        """

        config_read = configparser.ConfigParser()
        config_read.read_file(open('config.ini'))
        default_config = config_read['CONFIG']

        self.file_name = default_config['file_name']
        self.file_name = default_config['abaqus_file_path']

    def create_config(self):
        """Creating Config
        ===================
        Responsible for creating basic config for project.

        Two parameters:
        1. File Name
        2. File Path
        """

        config_create = configparser.ConfigParser()
        config_create['CONFIG'] = {'file_name': 'ceaDatabase',
                                   'abaqus_file_path': 'C:\\TEMP\\'}

        with open('config.ini', 'w') as created_config_file:
            config_create.write(created_config_file)

        self.file_name = 'ceaDatabase'
        self.abaqus_file_path = 'C:\\TEMP\\'

