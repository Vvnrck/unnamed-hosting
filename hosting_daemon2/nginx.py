import socket
import fcntl
import struct

from pathlib import Path
from docker_compose import DockerCompose


UPSTREAM_TEMPLATE = \
"""
upstream {app_name} {{
  server {host_ip}:{app_port};
}}
"""
SERVER_TEMPLATE = \
"""
server {{
    server_name {app_name}.{hosting_base};
    location / {{
        proxy_pass http://{app_name};
    }}
}}
"""
HOSTING_BASE = 'derhostar.io'
NGINX_PATH = Path('./url_resolver/')
SETTINGS_FILE = NGINX_PATH / 'config/nginx/settings.conf'


def _get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def _prepare_conf(apps):
    upstreams = []
    servers = []
    host_ip = _get_ip_address(b'docker0')
    
    for app in apps:
        port = app.exposed_port
        upstreams.append(UPSTREAM_TEMPLATE.format(
            app_name=app.name,
            host_ip=host_ip,
            app_port=port
        ))
        servers.append(SERVER_TEMPLATE.format(
            app_name=app.name,
            hosting_base=HOSTING_BASE
        ))
    
    upstreams = '\n'.join(upstreams)
    servers = '\n'.join(servers)
    return '{}\n{}'.format(upstreams, servers)


def _read_conf_file():
    with SETTINGS_FILE.open(mode='r') as conf:
        return conf.read()


def _write_conf_file(confdata):
    with SETTINGS_FILE.open(mode='w') as conf:
        conf.write(confdata)
        

def make_nginx_running(apps):
    conf = _prepare_conf(apps)
    if conf != _read_conf_file():
        _write_conf_file(conf)
        docker_nginx = DockerCompose(path=NGINX_PATH)
        if docker_nginx.ps():
            docker_nginx.restart()
        else:
            docker_nginx.up()
        

def restart_nginx():
    docker_nginx = DockerCompose(path=NGINX_PATH)
    if docker_nginx.ps():
        docker_nginx.restart()
    else:
        docker_nginx.up()

