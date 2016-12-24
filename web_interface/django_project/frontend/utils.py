import base64
import string
import random


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