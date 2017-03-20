import logging
import re
import subprocess
import sys

from datetime import datetime
from itertools import dropwhile, takewhile


logger = logging.getLogger('compose')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s| %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)


class DockerParsingError(Exception): pass


class DockerCompose:
    def __init__(self, path):
        self.path = str(path)
        logger.debug('docker created at %s', self.path)

    def ps(self):
        response = subprocess.Popen(
            ['docker-compose', 'ps'], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        response = str(response, 'utf-8')
        response = [line for line in response.split('\n') if line]
        response = response[2:]  # drop headers
        logger.debug('PS at %s -> len %s', self.path, len(response))
        return response
        
    def is_up(self):
        regexp = re.compile(r'Exit -?[0-9]+')
        services = self.ps()
        id_down = any(regexp.search(s) for s in services)
        is_up = not id_down
        logger.debug('IS_UP at %s -> %s', self.path, is_up)
        return is_up

    def port(self, service_name, private_port):
        logger.debug('PORT at %s', self.path)
        response = subprocess.Popen(
            ['docker-compose', 'port', service_name, private_port], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        response = str(response, 'utf-8')
        try:
            host, port = response.split(':')
            return port.strip('\n')
        except ValueError:
            logger.warning('Looks like %s is down', self.path)
            raise DockerParsingError('Looks like %s is down' % self.path)

    def up(self, daemon=True):
        logger.debug('UP at %s', self.path)
        response = subprocess.Popen(
            ['docker-compose', 'up', '-d'] if daemon
            else ['docker-compose', 'up'], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')

    def stop(self):
        logger.debug('STOP at %s', self.path)
        response = subprocess.Popen(
            ['docker-compose', 'stop'], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')
        
    def exec(self, service_name, command, args=tuple()):
        raise NotImplementedError
        
    def build(self, service_name=None):
        raise NotImplementedError
        
    def restart(self, service_name=None):
        logger.debug('RESTART at %s', self.path)
        response = subprocess.Popen(
            ['docker-compose', 'restart', service_name] if service_name
            else ['docker-compose', 'restart'], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')
        
    def last_accessed(self) -> 'minutes ago':
        logs = self.logs(timestamps=False, tail=1)
        logs = [log for log in logs.split('\n') if log.startswith('nginx')]
        if not logs:
            return 0
        log = logs[-1]
        log = dropwhile(lambda c: c != '[', log)
        log = takewhile(lambda c: c != ']', log)
        last_access_date = datetime.strptime(
            ''.join(log), '[%d/%b/%Y:%H:%M:%S %z'
        )
        now = datetime.now(tz=last_access_date.tzinfo)
        return (now - last_access_date).seconds // 60  

    def logs(self, no_color=True, timestamps=True, tail=1000):
        logger.debug('LOGS at %s (%s lines)', self.path, tail)
        call_args = list(filter(bool, [
            'docker-compose', 'logs',
            '--no-color' if no_color else None,
            '--timestamps' if timestamps else None, 
            '--tail={}'.format(tail)
        ]))
        response = subprocess.Popen(
            call_args,
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')

