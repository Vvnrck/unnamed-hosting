import json
import logging
import sys

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


logger = logging.getLogger('db_api')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s| %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)


class RemoteHostingDatabase:

    def __init__(self, creds_getter, settings):
        self.settings = settings
        self.auth_cookies = ''
        self.creds_getter = creds_getter

    def login(self) -> 'cookies':
        logger.debug('Logging into API')
        user, password = self.creds_getter()

        def cookie(header):
            key, val = header
            return key == 'Set-Cookie'

        post = Request(self.settings.API_METHOD['login'], urlencode({
            'username': user, 'password': password
        }).encode())
        response = urlopen(post)
        cookies = (h for h in response.getheaders() if cookie(h))
        cookies = (val for hdr, val in cookies)
        cookies = (c.split(';')[0] for c in cookies)
        cookies = '; '.join(cookies)
        self.auth_cookies = cookies
        return self.auth_cookies

    def do_request(self, method, *request_args, **request_kwargs):
        if not self.auth_cookies:
            self.login()

        response_body = {}
        for i in range(2):
            request = Request(method, *request_args, **request_kwargs)
            request.add_header('Cookie', self.auth_cookies)
            logger.debug('Request to %s', request.get_full_url())
            response = urlopen(request)
            response_body = response.read()
            response_body = str(response_body, 'utf-8')
            response_body = json.loads(response_body)

            if response_body.get('error') == 'login_required':
                logger.debug('Login required')
                self.login()
            else:
                break
        return response_body

    def do_request_ex(self, *args, **kwargs):
        try:
            return self.do_request(*args, **kwargs)
        except (URLError, HTTPError) as e:
            logger.error('Error occured: %s', repr(e))
            return {}

    def get_apps_to_enable(self):
        return self.do_request_ex(self.settings.API_METHOD['apps-to-enable'])

    def get_apps_to_disable(self):
        return self.do_request_ex(self.settings.API_METHOD['apps-to-disable'])

    def get_apps_to_deploy(self):
        return self.do_request_ex(self.settings.API_METHOD['apps-to-deploy'])


if __name__ == '__main__':
    import settings
    comm = RemoteHostingDatabase(lambda: ('admin', 'admin'), settings)
    print(comm.get_apps_to_enable())
    print(comm.get_apps_to_disable())
    print(comm.get_apps_to_deploy())
