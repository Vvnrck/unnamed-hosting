import sys
import json
import urllib.request

from apps import create_app, BaseApp
from nginx import make_nginx_running, restart_nginx
from docker_compose import DockerCompose

API_BASE = 'http://localhost:8888/api'
API_SHOULD_ENABLE_APPS = API_BASE + '/apps-to-enable'

        
def get_apps_to_enable():
    response = urllib.request.urlopen(API_SHOULD_ENABLE_APPS).read()
    response = str(response, 'utf-8')
    response = json.loads(response)
    apps = response.get('response', [])
    return [create_app(app) for app in apps]
    

def stop_all_apps():
    app_home = BaseApp.APPS_HOME
    app_paths = app_home.glob('*/*')
    app_paths = filter(lambda p: p.is_dir(), app_paths)
    composers = map(DockerCompose, app_paths)
    for compose in composers:
        print('Stopping', str(compose.path))
        compose.stop()
    
        
if __name__ == '__main__':
    if 'enable' in sys.argv:
        apps = get_apps_to_enable()
        for app in apps:
            app.prepare_app_folders()
            app.git_clone_app_code()
            app.make_docker_files()
            app.start_app(is_daemon=True)
            # app.docker_compose.stop()
            # app.docker_compose.up()
            print(app.exposed_port)
        make_nginx_running(apps)
        
    if 'disable' in sys.argv:
        stop_all_apps()
        
    if 'restart_nginx' in sys.argv:
        restart_nginx()

