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
        return port


    def up(self):
        response = subprocess.Popen(
            ["docker-compose", "up", "-d"], 
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

