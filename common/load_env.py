from os.path import dirname, abspath

from dotenv import load_dotenv

project_directory = dirname(dirname(abspath(__file__)))


def get_environment_variables():
    with open(f'{project_directory}/config/.env', 'r') as env:
        variables = {}
        for line in env.readlines():
            variable = [temp.strip() for temp in line.split("=")]
            if len(variable) == 2:
                variables[variable[0]] = variable[1]
        return variables


def load_custom_variables(values, force_write=False):
    variables = get_environment_variables() if not force_write else None
    with open(f'{project_directory}/config/.env', 'a') as env:
        for key, value in values.items():
            variable = f'\n{key}={value}'
            if not force_write:
                if key not in variables:
                    env.write(variable)
            else:
                env.write(variable)


def get_custom_variables():
    return {
        'PROJECT_DIRECTORY': project_directory
    }


def load_env():
    env_path = f'{project_directory}/config/.env'
    load_custom_variables(get_custom_variables())
    load_dotenv(dotenv_path=env_path)
