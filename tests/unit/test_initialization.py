# test script
import django
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

base_settings = {
    'ENVIRONMENT': 'dev',
    'DEBUG': True,
    'ROOT_URLCONF': 'demo_project.urls',
    'SECRET_KEY': 'test-key',
    'INSTALLED_APPS': ('django.contrib.auth', 'django.contrib.contenttypes', 'openapi_tester'),
    'DATABASES': {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3',}},
    'OPENAPI_TESTER': {'PATH': 'http://127.0.0.1:8080/swagger/?format=openapi', 'CASE': 'CAMELCASE'},
}


def test_successful_initialization(settings):
    django_settings.configure(**base_settings)
    django.setup()


def test_missing_package_settings(settings):
    """
    We need settings to run tests, therefore missing settings should raise an error.
    """
    test_settings = base_settings
    del test_settings['OPENAPI_TESTER']
    django_settings.configure(**test_settings)
    with pytest.raises(ImproperlyConfigured):
        django.setup()


def test_missing_path_setting(settings):
    """
    Path param is required, and should raise an error when missing
    """
    test_settings = base_settings
    del test_settings['OPENAPI_TESTER']['PATH']
    django_settings.configure(**test_settings)
    with pytest.raises(ImproperlyConfigured):
        django.setup()


def test_missing_case_settings(settings):
    """
    Missing case will default to camelCase and shouldn't raise an error.
    """
    test_settings = base_settings
    del test_settings['OPENAPI_TESTER']['CASE']
    django_settings.configure(**test_settings)
    django.setup()


def test_excess_settings(settings):
    """
    An error should be raised if OPENAPI_TESTER contains excess settings.
    """
    test_settings = base_settings
    test_settings['OPENAPI_TESTER']['test'] = 'test'
    django_settings.configure(**test_settings)
    with pytest.raises(ImproperlyConfigured):
        django.setup()

    # def test_badly_configured_path(self):
    #     """
    #     Missing case will default to camelCase and shouldn't raise an error.
    #     """
    #     for item in ['', None, [], {}, 2, 2.2]:
    #         test_settings = base_settings
    #         test_settings['OPENAPI_TESTER']['PATH'] = item
    #         settings.configure(**test_settings)
    #         with pytest.raises(ImproperlyConfigured):
    #             django.setup()
    #
    # def test_badly_configured_case(self):
    #     """
    #     Missing case will default to camelCase and shouldn't raise an error.
    #     """
    #     for item in ['', None, [], {}, 2, 2.2]:
    #         test_settings = base_settings
    #         test_settings['OPENAPI_TESTER']['PATH'] = item
    #         settings.configure(**test_settings)
    #         with pytest.raises(ImproperlyConfigured):
    #             django.setup()
