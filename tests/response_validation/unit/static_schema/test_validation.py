import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.static_schema.base import LoadStaticSchema


def test_validation(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    path = django_settings.BASE_DIR + '/demo_project/openapi-schema.yml'
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': path})
    base = LoadStaticSchema('api/v1/trucks/correct', 200, 'get')
    assert base.path == path


def test_drf_yasg_not_installed(monkeypatch):
    """
    Verify that validation raises an exception if the package isnt installed.
    """
    path = django_settings.BASE_DIR + '/demo_project/openapi-schema.yml'
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': path})
    import sys

    # Mock away the drf_yasg dependency
    temp = sys.modules['yaml']
    sys.modules['yaml'] = None

    with pytest.raises(ImproperlyConfigured, match='The package `PyYAML` is required for parsing yaml files. '
                                                   'Please run `pip install PyYAML` to install it.'):
        LoadStaticSchema('api/v1/trucks/correct', 200, 'get')

    sys.modules['yaml'] = temp


def test_missing_path():
    """
    Verify that validation runs successfully for the demo project.
    """
    with pytest.raises(ImproperlyConfigured, match='\`PATH\` is required when testing static schemas. '
                                                   'Please update your SWAGGER_TESTER settings.'):
        LoadStaticSchema('api/v1/trucks/correct', 200, 'get')


def test_bad_path_type(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': 2})
    with pytest.raises(ImproperlyConfigured, match='`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.'):
        LoadStaticSchema('api/v1/trucks/correct', 200, 'get')
