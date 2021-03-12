def config():
    try:
        read_config()

    except IOError:
        create_config()


def read_config():
    """Reading Config
    ==================

    If there is a config file, than it reads its content

    Reading:
    1. File Name
    2. File Path

    """

    config_read = open('config.ini')

    config_table = []

    for line in config_read:
        config_table.append(line.split(' = '))
        print line

    print config_table

    # TODO -> properties -> dictionary


def create_config():
    """Creating Config
    ===================
    Responsible for creating basic config for project.

    Two parameters:
    1. File Name
    2. File Path
    """

