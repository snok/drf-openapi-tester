# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest

from django_openapi_response_tester.configuration import SwaggerTesterSettings


def test_valid_settings() -> None:
    """
    Assert that the default settings in the demo project pass without errors.
    """
    SwaggerTesterSettings().validate()


def test_empty_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when empty OPENAPI_RESPONSE_TESTER dict is specified.
    """
    monkeypatch.setattr(django_settings, 'OPENAPI_RESPONSE_TESTER', {})
    with pytest.raises(ImproperlyConfigured, match='OPENAPI_RESPONSE_TESTER settings need to be configured'):
        SwaggerTesterSettings().validate()


def test_missing_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when no OPENAPI_RESPONSE_TESTER dict is specified.
    """
    monkeypatch.delattr(django_settings, 'OPENAPI_RESPONSE_TESTER')
    with pytest.raises(
        ImproperlyConfigured,
        match='OPENAPI_RESPONSE_TESTER settings need to be configured',
    ):
        SwaggerTesterSettings().validate()
