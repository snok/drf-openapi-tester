import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.loaders import StaticSchemaLoader
from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import yml_path


def test_static_schema_loader_validation(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader})
    settings = SwaggerTesterSettings()
    assert settings.loader_class.path == yml_path


def test_drf_yasg_not_installed(monkeypatch):
    """
    Verify that validation raises an exception if the package isnt installed.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader})
    import sys

    # Mock away the drf_yasg dependency
    temp = sys.modules['yaml']
    sys.modules['yaml'] = None

    with pytest.raises(
        ImproperlyConfigured,
        match='The package `PyYAML` is required for parsing yaml files. ' 'Please run `pip install PyYAML` to install it.',
    ):
        SwaggerTesterSettings()

    sys.modules['yaml'] = temp


def test_missing_path(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'SCHEMA_LOADER': StaticSchemaLoader})
    with pytest.raises(
        ImproperlyConfigured,
        match='PATH is required to load static OpenAPI schemas. Please add PATH to the SWAGGER_TESTER settings',
    ):
        SwaggerTesterSettings()


def test_bad_path_type(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': 2, 'SCHEMA_LOADER': StaticSchemaLoader})
    with pytest.raises(
        ImproperlyConfigured, match='`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.'
    ):
        SwaggerTesterSettings()
