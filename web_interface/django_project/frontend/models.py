import enum

from django.db import models
from django.contrib.auth.models import User

from . import utils
# Create your models here.


class AppStates(enum.Enum):
    enabled = 'enabled'
    disabled = 'disabled'
    paused = 'paused'

    @staticmethod
    def except_enabled():
        return tuple(s for s in AppStates if s != AppStates.enabled) + (None,)

    @staticmethod
    def except_disabled():
        return tuple(s for s in AppStates if s != AppStates.disabled) + (None,)

    @staticmethod
    def except_paused():
        return tuple(s for s in AppStates if s != AppStates.paused) + (None,)


class AppType(enum.Enum):
    static = 'static'
    flask = 'flask'


class App(models.Model):
    owner = models.ForeignKey(User)

    name = models.CharField(max_length=128, unique=True)
    db_user = models.CharField(max_length=128, unique=True)
    db_pass = models.CharField(max_length=128)
    repo_url = models.CharField(max_length=4096)
    app_type = models.CharField(max_length=128)

    app_path = models.CharField(max_length=4096, null=True)
    app_url = models.CharField(max_length=4096, null=True)
    desired_state = models.CharField(max_length=128, default=AppStates.enabled)
    current_state = models.CharField(max_length=128, null=True)
    image_id = models.CharField(max_length=4096, null=True)
    container_id = models.CharField(max_length=4096, null=True)

    restart_required = models.BooleanField(default=False)
    deploy_required = models.BooleanField(default=False)

    @staticmethod
    def new_app(owner: User, app_name, repo_url, app_type):
        app = App.objects.create(
            owner=owner,
            name=app_name,
            repo_url=repo_url,
            app_type=app_type,
            db_user=utils.generate_db_user(owner.username, app_name),
            db_pass=utils.generate_db_password(),
            app_path=utils.generate_app_path(owner.username, app_name)
        )
        app.save()
