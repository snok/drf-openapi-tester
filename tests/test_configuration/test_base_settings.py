# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_settings


def test_valid_settings() -> None:
    """
    Assert that the default settings in the demo project pass without errors.
    """
    SwaggerTesterSettings()


def test_empty_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when empty SWAGGER_TESTER dict is specified.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {})
    with pytest.raises(ImproperlyConfigured, match='SWAGGER_TESTER settings need to be configured'):
        SwaggerTesterSettings()


def test_missing_settings(monkeypatch) -> None:
    """
    Asserts that no error is raised when no SWAGGER_TESTER dict is specified.
    """
    monkeypatch.delattr(django_settings, 'SWAGGER_TESTER')
    with pytest.raises(
        ImproperlyConfigured,
        match='Please configure SWAGGER_TESTER in your settings or remove ' 'django-swagger-tester as a dependency',
    ):
        SwaggerTesterSettings()


def test_excess_settings_pass_silently(monkeypatch) -> None:
    """
    Excess settings are allowed at the top level, since some loader classes require extra settings.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('bad_setting', 5))
    SwaggerTesterSettings()
