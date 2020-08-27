from copy import deepcopy

from django.conf import settings as django_settings

default_settings = django_settings.SWAGGER_TESTER
default_middleware_settings = default_settings['MIDDLEWARE']


def patch_settings(key, value) -> dict:
    patched_settings = deepcopy(default_settings)
    patched_settings[key] = value
    return patched_settings


def patch_middleware_settings(key, value) -> dict:
    patched_middleware_settings = deepcopy(default_middleware_settings)
    patched_middleware_settings[key] = value
    settings = deepcopy(default_settings)
    settings['MIDDLEWARE'] = patched_middleware_settings
    return settings


yml_path = str(django_settings.BASE_DIR) + '/static_schemas/openapi-schema.yml'
json_path = str(django_settings.BASE_DIR) + '/static_schemas/openapi-schema.json'
