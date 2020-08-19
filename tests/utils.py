from django.conf import settings as django_settings

default_settings = django_settings.SWAGGER_TESTER


def patch_settings(key, value):
    patched_settings = default_settings
    patched_settings[key] = value
    return patched_settings
