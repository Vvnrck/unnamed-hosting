import logging
import sys
import settings

from apps import create_app
from nginx import make_nginx_running, restart_nginx
from docker_compose import DockerCompose
from db_api import RemoteHostingDatabase


communicator = RemoteHostingDatabase(lambda: ('admin', 'admin'), settings)

logger = logging.getLogger('scenarios')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s| %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)


def start_apps():
    logger.debug('start_apps started')
    apps = communicator.get_should_be_running_apps()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    for app in apps:
        app.docker_compose.up()
    logger.debug('start_apps finished')


def deploy_apps():
    logger.debug('deploy_apps started')
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
    logger.debug('deploy_apps finished')
    

def enable_apps():
    logger.debug('enable_apps started')
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
    logger.debug('enable_apps finished')
    

def disable_apps():
    logger.debug('disable_apps started')
    apps = communicator.get_apps_to_disable()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    for app in apps:
        app.docker_compose.stop()
    update_reverse_proxy()
    communicator.set_apps_status(apps)
    logger.debug('disable_apps finished')
    

def update_reverse_proxy():
    apps = communicator.get_should_be_running_apps()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    make_nginx_running(apps)


def revisit_running_apps():
    logger.debug('revisit_running_apps started')
    apps = communicator.get_should_be_running_apps()
    apps = apps.get('response', [])
    apps = [create_app(app) for app in apps]
    apps = [app for app in apps if app.is_running]
    for app in apps:
        logs = app.docker_compose.logs()
        communicator.post_logs(app, logs)
    communicator.set_apps_status(apps)
    logger.debug('revisit_running_apps finished')

