# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from django_swagger_tester.schema_loaders import DrfYasgSchemaLoader, StaticSchemaLoader
from tests.utils import patch_settings


def test_valid_loader_classes(monkeypatch) -> None:
    """
    Assert that valid cases always pass without errors.
    """
    for case in [DrfYasgSchemaLoader, StaticSchemaLoader]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', case))
        SwaggerTesterSettings()


def test_missing_loader_class(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', None))
    with pytest.raises(
        ImproperlyConfigured,
        match='SCHEMA_LOADER is missing from your SWAGGER_TESTER settings, '
        'and is required. '
        'Please pass a loader class from django_swagger_tester.schema_loaders',
    ):
        SwaggerTesterSettings()


def test_invalid_invalid_callable(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', lambda x: x))
    with pytest.raises(ImproperlyConfigured, match='SCHEMA_LOADER must be a class'):
        SwaggerTesterSettings()


def test_invalid_base_class(monkeypatch) -> None:
    class BadClass:
        pass

    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', BadClass))
    with pytest.raises(
        ImproperlyConfigured,
        match='The supplied LOADER_CLASS must inherit django_swagger_tester.schema_loaders._LoaderBase',
    ):
        SwaggerTesterSettings()
