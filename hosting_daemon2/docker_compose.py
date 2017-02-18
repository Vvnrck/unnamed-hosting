import logging
import re
import subprocess
import sys


logger = logging.getLogger('compose')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s| %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)


class DockerCompose:
    def __init__(self, path):
        self.path = str(path)
        logger.debug('docker created at %s', self.path)

    def ps(self):
        response = subprocess.Popen(
            ["docker-compose", "ps"], 
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
            ["docker-compose", "port", service_name, private_port], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        response = str(response, 'utf-8')
        host, port = response.split(':')
        return port.strip('\n')

    def up(self, daemon=True):
        logger.debug('UP at %s', self.path)
        response = subprocess.Popen(
            ["docker-compose", "up", "-d"] if daemon
            else ["docker-compose", "up"], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')

    def stop(self):
        logger.debug('STOP at %s', self.path)
        response = subprocess.Popen(
            ["docker-compose", "stop"], 
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
            ["docker-compose", "restart", service_name] if service_name
            else ["docker-compose", "restart"], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')

