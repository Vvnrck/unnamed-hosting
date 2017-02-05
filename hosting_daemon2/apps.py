import shutil
import subprocess

from pathlib import Path
from docker_compose import DockerCompose


def create_app(json_description):
    app_class = json_description['app_type']
    return {
        'flask': FlaskApp
    }[app_class](json_description)


class BaseApp:
    APPS_HOME = Path('./user_apps')
    DOCKER_TEMPLATES = NotImplemented
    APP_PORT = NotImplemented

    def __init__(self, json_description):
        self.app_type = json_description['app_type']
        self.path = self.APPS_HOME / json_description['app_path']
        self.app_url = json_description['app_url']
        self.repo_url = json_description['repo_url']

        self.docker_file = self.DOCKER_TEMPLATES / 'Dockerfile'
        self.docker_compose_file = self.DOCKER_TEMPLATES / 'docker-compose.yml'
        self.docker_compose = DockerCompose(self.path)
    
    @property
    def is_running(self):
        return bool(self.docker_compose.ps())
        
    @property
    def exposed_port(self):
        return self.docker_compose.port('web', self.APP_PORT)
        
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


class FlaskApp(BaseApp):
    DOCKER_TEMPLATES = Path('./docker_templates/flask')
    APP_PORT = "5000"
    
    def __init__(self, *args):
        super().__init__(*args)
        
    def make_docker_files(self):
        shutil.copy(str(self.docker_file), str(self.path))
        shutil.copy(str(self.docker_compose_file), str(self.path))
        
    def start_app(self):
        if self.docker_compose.ps():
            self.docker_compose.stop()
        self.docker_compose.up()
