import sys
import settings

from apps import create_app
from nginx import make_nginx_running, restart_nginx
from docker_compose import DockerCompose
from db_api import RemoteHostingDatabase


communicator = RemoteHostingDatabase(lambda: ('admin', 'admin'), settings)


def deploy_apps():
    apps = communicator.get_apps_to_deploy()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    for app in apps:
        app.prepare_app_folders()
        app.git_clone_app_code()
        app.make_docker_files()
        app.start_app(is_daemon=True)
        app.docker_compose.stop()
        app.docker_compose.up()
        print(app.exposed_port)
    update_reverse_proxy()
    communicator.set_apps_status(apps)
    

def enable_apps():
    apps = communicator.get_apps_to_enable()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    for app in apps:
        app.prepare_app_folders()
        app.git_clone_app_code()
        app.make_docker_files()
        app.start_app(is_daemon=True)
        print(app.exposed_port)
    update_reverse_proxy()
    communicator.set_apps_status(apps)
    

def disable_apps():
    apps = communicator.get_apps_to_disable()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    for app in apps:
        app.docker_compose.stop()
    update_reverse_proxy()
    communicator.set_apps_status(apps)
    

def update_reverse_proxy():
    apps = communicator.get_should_be_running_apps()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    make_nginx_running(apps)


def revisit_running_apps():
    apps = communicator.get_should_be_running_apps()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    apps = [app for app in apps if app.is_running]
    for app in apps:
        logs = app.docker_compose.logs()
        communicator.post_logs(app, logs)

