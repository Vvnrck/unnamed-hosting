import base64
import string
import random

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse


def generate_db_user(owner_name, app_name):
    salted = '{}::{}'.format(owner_name, app_name)
    salted = bytes(salted, encoding='utf-8')
    hashed = base64.encodebytes(salted)
    hashed = str(hashed, encoding='utf-8')
    return hashed


def generate_db_password(length=16):
    pool = string.ascii_letters + string.digits + '!@#$%^&*()_+=~'
    return ''.join(random.choice(pool) for _ in range(length))


def generate_app_path(owner_name, app_name):
    return '{}/{}'.format(owner_name, app_name)


# Decorators:

def debug_only(func):
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            return HttpResponseBadRequest()
        return func(*args, **kwargs)
    return wrapper


def post_only(func):
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG and request.method != 'POST':
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)
    return wrapper


def authenticated_only(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse(content=b'{"error": "login_required"}')
    return wrapper
