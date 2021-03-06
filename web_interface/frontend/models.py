import enum
import pathlib

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from . import utils
# Create your models here.


class AppStates(enum.Enum):
    enabled = 'enabled'
    disabled = 'disabled'
    paused = 'paused'

    deploy_needed = 'first_run_waiting'
    delete_needed = 'delete_needed'

    err_hook_not_found = 'hooks.json not found'
    err_launch_crashed = 'launch has crashed'


class AppType(enum.Enum):
    static = 'static'
    flask = 'flask'
    django = 'django'


class App(models.Model):
    owner = models.ForeignKey(User, related_name='apps')  # make nullable. Don't delete apps

    name = models.CharField(max_length=128, unique=True)
    repo_url = models.CharField(max_length=4096)
    app_type = models.CharField(max_length=128)
    app_path = models.CharField(max_length=4096, null=True)
    app_url = models.CharField(max_length=4096, null=True)
    desired_state = models.CharField(max_length=128, default=AppStates.deploy_needed)
    current_state = models.CharField(max_length=128, null=True)

    restart_required = models.BooleanField(default=False)
    deploy_required = models.BooleanField(default=False)

    @staticmethod
    def new_app(owner: User, app_name, repo_url, app_type):
        app = App.objects.create(
            owner=owner,
            name=app_name,
            repo_url=repo_url,
            app_type=app_type,
            app_path=utils.generate_app_path(owner.username, app_name)
        )
        
        with app.log_file_path.open(mode='w') as logs:
            logs.write('no one has submitted logs yet')
            
        Notification.objects.create(
            app=app,
            message='{} has been created'.format(str(app))
        )
        
        app.save()
        return app
        
    def __str__(self):
        return '{} (id={}, owner={}, curst={}, desst={})'.format(
            self.name, str(self.id), self.owner,
            self.current_state, self.desired_state
        )

    @property
    def shorter_repo_url(self):
        limit = 40
        if len(self.repo_url) <= limit:
            return self.repo_url
        return str(self.repo_url)[:limit - 3] + '...'
        
    @property
    def log_file_path(self) -> pathlib.Path:
        return self.log_file_dir / 'logs.txt'
        
    @property
    def log_file_dir(self) -> pathlib.Path:
        dir_ = pathlib.Path(settings.APP_LOGS_ROOT) / self.app_path
        if not dir_.exists():
            dir_.mkdir(parents=True)
        return pathlib.Path(settings.APP_LOGS_ROOT) / self.app_path 

    def as_dict(self):
        exposed_fields = (
            'id', 'name', 'repo_url', 'app_type', 'app_path',
            'desired_state', 'current_state'
        )
        return {field: getattr(self, field) for field in exposed_fields}


class LogRequest(models.Model):
    app = models.OneToOneField(App)
    log_uploaded = models.BooleanField(default=False)

    @staticmethod
    def get_or_create_log_request(app_id):
        app = App.objects.get(id=app_id)
        folder = pathlib.Path(settings.APP_LOGS_ROOT) / app.app_path
        if not folder.exists():
            folder.mkdir(parents=True)
        lr, _ = LogRequest.objects.get_or_create(app=app)
        return lr

    @property
    def log_file_path(self):
        return pathlib.Path(settings.APP_LOGS_ROOT) / self.app.app_path / 'logs.txt'

    def upload_file(self, binary_data):
        with self.log_file_path.open(mode='w') as log:
            log.write(binary_data)
        self.log_uploaded = True
        self.save()

    def read_file(self):
        if not self.log_uploaded:
            return None

        path = self.log_file_path
        with path.open(mode='r') as log:
            data = log.read()
        self.log_uploaded = False
        return data


class Notification(models.Model):
    app = models.ForeignKey(App)
    message = models.CharField(max_length=4096)
    received_at = models.DateTimeField(auto_now=True)

    
