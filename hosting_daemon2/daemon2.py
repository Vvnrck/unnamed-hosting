import json
import urllib.request
import subprocess
import shutil

from collections import namedtuple
from pathlib import Path

API_BASE = 'http://localhost:8000/api'
API_SHOULD_ENABLE_APPS = API_BASE + '/apps-to-enable'


class App:
    APPS_HOME = Path('.')

    def __init__(self, json_description):
        self.app_type = json_description['app_type']
        self.path = App.APPS_HOME / json_description['app_path']
        self.app_url = json_description['app_url']
        self.repo_url = json_description['repo_url']
        
    def prepare_app_folders(self):
        try:
            self.path.mkdir(parents=True)
        except FileExistsError as e:
            print(e)
        print('to be deleted:', str(self.path))
        shutil.rmtree(str(self.path))
   
    def _git_clone_app_code(self):
        pass
        

def get_apps_to_enable():
    response = urllib.request.urlopen(API_SHOULD_ENABLE_APPS).read()
    response = str(response, 'utf-8')
    response = json.loads(response)
    apps = response.get('response', [])
    return [App(app) for app in apps]
    
        
if __name__ == '__main__':
    apps = get_apps_to_enable()
    for app in apps:
        app.prepare_app_folders()
