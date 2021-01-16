import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from openapi_tester.configuration import OpenAPITesterSettings
from openapi_tester.loaders import StaticSchemaLoader
from tests import yml_path


def test_static_schema_loader_validation():
    """
    Verify that validation runs successfully for the test_project.
    """
    with override_settings(OPENAPI_TESTER={'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader}):
        settings = OpenAPITesterSettings()
        assert settings.loader_class.path == yml_path


def test_missing_path():
    """
    Verify that validation runs successfully for the test_project.
    """
    with override_settings(OPENAPI_TESTER={'SCHEMA_LOADER': StaticSchemaLoader}):
        with pytest.raises(
            ImproperlyConfigured,
            match='PATH is required to load static OpenAPI schemas. Please add PATH to the OPENAPI_TESTER settings',
        ):
            OpenAPITesterSettings().validate()


def test_bad_path_type():
    """
    Verify that validation runs successfully for the test_project.
    """
    with override_settings(OPENAPI_TESTER={'PATH': 2, 'SCHEMA_LOADER': StaticSchemaLoader}):
        with pytest.raises(
            ImproperlyConfigured, match='`PATH` needs to be a string. Please update your OPENAPI_TESTER settings.'
        ):
            OpenAPITesterSettings().validate()
