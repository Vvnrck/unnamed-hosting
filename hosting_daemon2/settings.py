HOST = 'http://localhost:8888'
API_URL = HOST + '/api'
API_METHOD = {
    'login': API_URL + '/login',
    'apps-to-enable': API_URL + '/apps-to-enable',
    'apps-to-disable': API_URL + '/apps-to-disable',
    'apps-to-deploy': API_URL + '/apps-to-deploy',
    'set-apps-status': API_URL + '/set-apps-status',
    'apps-should-be-running': API_URL + '/apps-should-be-running',
    'get-all-apps': API_URL + '/all-apps'
}

HOSTING_BASE = 'derhostar.io'
APP_URL_TEMPLATE = '{0}.' + HOSTING_BASE

APP_LOG_FILENAME = '_app_log_file.0xfdda.txt'

