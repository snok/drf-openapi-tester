import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from openapi_tester.configuration import SwaggerTesterSettings


def test_valid_settings() -> None:
    """
    Assert that the default settings in the demo project pass without errors.
    """
    SwaggerTesterSettings().validate()


def test_empty_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when empty RESPONSE_TESTER dict is specified.
    """
    monkeypatch.setattr(django_settings, 'RESPONSE_TESTER', {})
    with pytest.raises(ImproperlyConfigured, match='RESPONSE_TESTER settings need to be configured'):
        SwaggerTesterSettings().validate()


def test_missing_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when no RESPONSE_TESTER dict is specified.
    """
    monkeypatch.delattr(django_settings, 'RESPONSE_TESTER')
    with pytest.raises(
        ImproperlyConfigured,
        match='RESPONSE_TESTER settings need to be configured',
    ):
        SwaggerTesterSettings().validate()
