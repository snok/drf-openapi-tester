# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_settings

from django_swagger_tester.configuration import SwaggerTesterSettings
from django_swagger_tester.loaders import DrfYasgSchemaLoader, StaticSchemaLoader


def test_valid_loader_classes(monkeypatch) -> None:
    """
    Assert that valid cases always pass without errors.
    """
    for case in [DrfYasgSchemaLoader, StaticSchemaLoader]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', case))
        SwaggerTesterSettings().validate()


def test_missing_loader_class(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', None))
    with pytest.raises(
        ImproperlyConfigured,
        match='SCHEMA_LOADER is missing from your SWAGGER_TESTER settings, '
        'and is required. '
        'Please pass a loader class from django_swagger_tester.schema_loaders',
    ):
        SwaggerTesterSettings().validate()


def test_invalid_invalid_callable(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', lambda x: x))
    with pytest.raises(ImproperlyConfigured, match='SCHEMA_LOADER must be a class'):
        SwaggerTesterSettings().validate()


def test_invalid_base_class(monkeypatch) -> None:
    class BadClass:
        pass

    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('SCHEMA_LOADER', BadClass))
    with pytest.raises(
        ImproperlyConfigured,
        match='The supplied loader_class must inherit django_swagger_tester.schema_loaders._LoaderBase',
    ):
        SwaggerTesterSettings().validate()
