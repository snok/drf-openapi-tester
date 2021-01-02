# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from tests.utils import patch_settings

from response_tester.configuration import SwaggerTesterSettings
from response_tester.loaders import DrfYasgSchemaLoader, StaticSchemaLoader


def test_valid_loader_classes(monkeypatch) -> None:
    """
    Assert that valid cases always pass without errors.
    """
    for case in [DrfYasgSchemaLoader, StaticSchemaLoader]:
        monkeypatch.setattr(django_settings, 'RESPONSE_TESTER', patch_settings('SCHEMA_LOADER', case))
        SwaggerTesterSettings().validate()


def test_missing_loader_class(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'RESPONSE_TESTER', patch_settings('SCHEMA_LOADER', None))
    with pytest.raises(
        ImproperlyConfigured,
        match='SCHEMA_LOADER is missing from your RESPONSE_TESTER settings, '
        'and is required. '
        'Please pass a loader class from response_tester.schema_loaders',
    ):
        SwaggerTesterSettings().validate()


def test_invalid_invalid_callable(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'RESPONSE_TESTER', patch_settings('SCHEMA_LOADER', lambda x: x))
    with pytest.raises(ImproperlyConfigured, match='SCHEMA_LOADER must be a class'):
        SwaggerTesterSettings().validate()


def test_invalid_base_class(monkeypatch) -> None:
    class BadClass:
        pass

    monkeypatch.setattr(django_settings, 'RESPONSE_TESTER', patch_settings('SCHEMA_LOADER', BadClass))
    with pytest.raises(
        ImproperlyConfigured,
        match='The supplied loader_class must inherit response_tester.schema_loaders._LoaderBase',
    ):
        SwaggerTesterSettings().validate()
