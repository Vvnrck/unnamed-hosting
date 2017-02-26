import os
import json
import shutil
import subprocess

import settings

from pathlib import Path
from docker_compose import DockerCompose


def create_app(json_description):
    app_class = json_description['app_type']
    return {
        'flask': FlaskApp,
        'django': DjangoApp
    }[app_class](json_description)

# TODO: create app validator


class BaseApp:
    APPS_HOME = Path('./user_apps')
    DOCKER_TEMPLATES = NotImplemented
    APP_SERVICE = NotImplemented
    APP_PORT = NotImplemented
    PROJECT_HOOKS_FILE = 'hooks.json'

    def __init__(self, json_description):
        self.name = json_description['name']
        self.app_type = json_description['app_type']
        self.path = self.APPS_HOME / json_description['app_path']
        self.app_url = settings.APP_URL_TEMPLATE.format(self.name)
        self.repo_url = json_description['repo_url']

        self.docker_file = self.DOCKER_TEMPLATES / 'Dockerfile'
        self.docker_compose_file = self.DOCKER_TEMPLATES / 'docker-compose.yml'
        self.docker_compose = DockerCompose(self.path)

        self._project_hooks = None
        
    def __repr__(self):
        return '{}(id={}, name={}, type={})'.format(
            type(self).__name__, 'NA', self.name, self.app_type
        )

    @property
    def is_running(self):
        return self.docker_compose.is_up()  # bool(self.docker_compose.ps())

    @property
    def exposed_port(self):
        return self.docker_compose.port(self.APP_SERVICE, self.APP_PORT)

    @property
    def project_hooks(self):
        if self._project_hooks is None:
            hooks = self.path / self.PROJECT_HOOKS_FILE
            with hooks.open() as hooks_file:
                self._project_hooks = json.load(hooks_file).get('hooks', {})
        return self._project_hooks

    def prepare_app_folders(self):
        if self.path.exists():
            shutil.rmtree(str(self.path))
        self.path.mkdir(parents=True)

    def git_clone_app_code(self):
        p = subprocess.Popen(
            ['git', 'clone', self.repo_url, '.'],
            cwd=str(self.path)
        )
        p.wait()

    def make_docker_files(self):
        raise NotImplementedError

    def start_app(self, is_daemon=True):
        if self.docker_compose.ps():
            self.docker_compose.stop()
        self.docker_compose.up(is_daemon)


class FlaskApp(BaseApp):
    DOCKER_TEMPLATES = Path('./docker_templates/flask')
    APP_SERVICE = 'web'
    APP_PORT = '5000'

    def __init__(self, *args):
        super().__init__(*args)

    def make_docker_files(self):
        shutil.copy(str(self.docker_file), str(self.path))
        shutil.copy(str(self.docker_compose_file), str(self.path))


class DjangoApp(BaseApp):
    DOCKER_TEMPLATES = Path('./docker_templates/django')
    APP_SERVICE = 'nginx'
    APP_PORT = '8000'

    def __init__(self, *args):
        super().__init__(*args)
        self.nginx_conf_dir = self.DOCKER_TEMPLATES / 'config'

    def make_docker_files(self):
        shutil.copy(str(self.docker_file), str(self.path))
        shutil.copy(str(self.docker_compose_file), str(self.path))

        shutil.copytree(str(self.nginx_conf_dir), str(self.path / 'config'))
        (self.path / 'static').mkdir()

        new_compose_path = self.path / self.docker_compose_file.name
        template = ''
        with new_compose_path.open('r') as text:
            template = text.read()
        wsgi_app = self.project_hooks['wsgi_app']
        with new_compose_path.open('w') as compose_file:
            compose_file.write(template.format(wsgi_app_name=wsgi_app))

    # def start_app(self):
        # build
        # run collectstatic
        # run
        # raise NotImplementedError



















