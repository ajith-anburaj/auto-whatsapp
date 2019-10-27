from os.path import dirname, abspath

from dotenv import load_dotenv


def load_custom_variables():
    pass


def load_env():
    project_directory = dirname(dirname(abspath(__file__)))
    env_path = f'{project_directory}/config/.env'
    load_dotenv(dotenv_path=env_path)
    load_custom_variables()
