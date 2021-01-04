import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from openapi_tester.configuration import OpenAPITesterSettings


def test_valid_settings() -> None:
    """
    Assert that the default settings in the demo project pass without errors.
    """
    OpenAPITesterSettings().validate()


def test_empty_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when empty OPENAPI_TESTER dict is specified.
    """
    monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {})
    with pytest.raises(ImproperlyConfigured, match='OPENAPI_TESTER settings need to be configured'):
        OpenAPITesterSettings().validate()


def test_missing_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when no OPENAPI_TESTER dict is specified.
    """
    monkeypatch.delattr(django_settings, 'OPENAPI_TESTER')
    with pytest.raises(
        ImproperlyConfigured,
        match='OPENAPI_TESTER settings need to be configured',
    ):
        OpenAPITesterSettings().validate()
