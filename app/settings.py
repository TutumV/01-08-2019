import pathlib
import yaml

JWT_SECRET_KEY = 'iwilldoit'
JWT_ALGORITHM = 'HS256'
SALT = '$2b$08$N5Ki85CXepNsxzmR1/9WWe'

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR  / 'config-local.yml'


def get_config(path):
    with open(path) as f:
        config = yaml.load(f)
    return config


config = get_config(config_path)
