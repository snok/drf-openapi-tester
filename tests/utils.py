from django.conf import settings as django_settings

default_settings = django_settings.SWAGGER_TESTER
default_middleware_settings = default_settings['MIDDLEWARE']


def patch_settings(key, value) -> dict:
    patched_settings = default_settings
    patched_settings[key] = value
    return patched_settings


def patch_middleware_settings(key, value) -> dict:
    patched_middleware_settings = default_middleware_settings
    patched_middleware_settings[key] = value
    settings = default_settings
    settings['MIDDLEWARE'] = patched_middleware_settings
    return settings
