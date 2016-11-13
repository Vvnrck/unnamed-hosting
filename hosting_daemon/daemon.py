import time
import logging
import subprocess
import sys

from collections import namedtuple

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(name='basic')


class ImageType:
    class Python:
        flask = 1
        dockerfile_template = '~/work/unnamed-hosting/images/flask/Dockerfile'


class ImageRequest:
    def __init__(self, imtype : ImageType, vcs_url : str):
        self.imtype = imtype
        self.vcs_url = vcs_url


def _docker_validate(docker_response):
    assert b'Cannot connect to the Docker daemon.' not in docker_response
    assert b'is not a docker command.' not in docker_response


def _docker_ps():
    ps = namedtuple('Ps', ['container_id', 'image_id'])
    apps_running = []

    data = subprocess.Popen(
        ["docker", "ps"], stdout=subprocess.PIPE
    ).communicate()[0]
    _docker_validate(data)
    data = str(data, 'utf-8')

    for line in filter(len, data.split('\n')[1:]):
        items = line.split()
        apps_running.append(ps(items[0], items[1]))
    return apps_running


def _docker_run(image_id):
    cmd = 'docker run -d -p 45000:5000 {image_id} ' + \
          'python /unnamed-hosting-sample-flask/app.py'
    data = subprocess.Popen(
        cmd.format(image_id=image_id).split(), stdout=subprocess.PIPE
    ).communicate()[0]
    _docker_validate(data)
    data = str(data, 'utf-8')
    return data


def _docker_stop(containers_id):
    data = subprocess.Popen(
        ['docker', 'stop'] + containers_id, stdout=subprocess.PIPE
    ).communicate()[0]
    _docker_validate(data)
    data = str(data, 'utf-8')
    return data


def get_running_apps() -> 'set of image IDs':
    image_ids = set()
    for app in _docker_ps():
        image_ids.add(app.image_id)
    logger.debug('Running images: %s' % image_ids)
    return image_ids


def get_apps_that_should_be_running() -> 'set of image IDs or image requests':
    image_ids = set()
    with open('images_to_run_stub', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line:
                image_ids.add(line)
    logger.debug('Should-be running images: %s' % image_ids)
    return image_ids


def run_app(image_id : str) -> 'container_id':
    logger.debug('Turning on image %s' % image_id)
    container_id = _docker_run(image_id)
    logger.debug('Got container %s' % container_id)
    return container_id


def get_apps_by_image_id(image_id : str) -> 'list of container IDs':
    container_ids = []
    for app in _docker_ps():
        if app.image_id == image_id:
            container_ids.append(app.container_id)
    return container_ids


def stop_apps(containers_id : list):
    logger.debug('Turning off containers %s' % containers_id)
    stopped_containers = _docker_stop(containers_id)
    logger.debug('Turned off containers %s' % stopped_containers)


def create_image(image_request : ImageRequest) -> 'image_id':
    return ''


def loop():
    logger.debug('Running app turn on/off')

    running_apps = get_running_apps()
    should_run = get_apps_that_should_be_running()
    turn_on_apps = should_run - running_apps
    turn_off_apps = running_apps - should_run

    for app in turn_on_apps:
        if isinstance(app, ImageRequest):
            app = create_image(app)
        run_app(app)

    for app in turn_off_apps:
        containers_id = get_apps_by_image_id(app)
        stop_apps(containers_id)

    time.sleep(5)


if __name__ == '__main__':
    while True:
        loop()

