from copy import deepcopy

from django.conf import settings as django_settings

default_settings = django_settings.SWAGGER_TESTER


def patch_settings(key, value) -> dict:
    patched_settings = deepcopy(default_settings)
    patched_settings[key] = value
    return patched_settings


yml_path = str(django_settings.BASE_DIR) + '/static_schemas/openapi-schema.yml'
json_path = str(django_settings.BASE_DIR) + '/static_schemas/openapi-schema.json'


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
