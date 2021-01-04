from copy import deepcopy

import yaml
from django.conf import settings as django_settings

from tests import yml_path


def patch_settings(key, value) -> dict:
    patched_settings = deepcopy(django_settings.OPENAPI_TESTER)
    patched_settings[key] = value
    return patched_settings


class MockRoute:
    def __init__(self, x):
        self.x = x
        self.counter = 0
        self.parameters = [2, 2]

    def get_path(self):
        self.counter += 1
        if self.counter == 2:
            raise IndexError
        return self.x


def ret_schema(*args, **kwargs):
    with open(yml_path) as f:
        content = f.read()
    return yaml.load(content, Loader=yaml.FullLoader)


def loader(path):
    with open(str(django_settings.BASE_DIR.parent) + path) as f:
        return yaml.load(f, Loader=yaml.FullLoader)
