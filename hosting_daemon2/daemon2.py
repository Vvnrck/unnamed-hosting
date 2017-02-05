import json
import urllib.request

from apps import create_app

API_BASE = 'http://localhost:8000/api'
API_SHOULD_ENABLE_APPS = API_BASE + '/apps-to-enable'

        
def get_apps_to_enable():
    response = urllib.request.urlopen(API_SHOULD_ENABLE_APPS).read()
    response = str(response, 'utf-8')
    response = json.loads(response)
    apps = response.get('response', [])
    return [create_app(app) for app in apps]
    
        
if __name__ == '__main__':
    apps = get_apps_to_enable()
    for app in apps:
        app.prepare_app_folders()
        app.git_clone_app_code()
        app.make_docker_files()
        app.start_app()
        print(app.exposed_port)

