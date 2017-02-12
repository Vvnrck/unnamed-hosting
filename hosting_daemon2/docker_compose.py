import subprocess


class DockerCompose:
    def __init__(self, path):
        self.path = str(path)

    def ps(self):
        response = subprocess.Popen(
            ["docker-compose", "ps"], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        response = str(response, 'utf-8')
        response = [line for line in response.split('\n') if line]
        response = response[2:]  # drop headers
        return response

    def port(self, service_name, private_port):
        response = subprocess.Popen(
            ["docker-compose", "port", service_name, private_port], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        response = str(response, 'utf-8')
        host, port = response.split(':')
        return port.strip('\n')

    def up(self, daemon=True):
        response = subprocess.Popen(
            ["docker-compose", "up", "-d"] if daemon
            else ["docker-compose", "up"], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')

    def stop(self):
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
        response = subprocess.Popen(
            ["docker-compose", "restart", service_name] if service_name
            else ["docker-compose", "restart"], 
            stdout=subprocess.PIPE,
            cwd=self.path
        ).communicate()[0]
        return str(response, 'utf-8')

