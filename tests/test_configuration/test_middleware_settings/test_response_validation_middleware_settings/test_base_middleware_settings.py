# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_response_validation_middleware_settings, patch_settings


def test_missing_middleware_settings(monkeypatch) -> None:
    """
    Assert that passing None or {} as middleware settings doesn't cause errors.
    """
    for value in [None, {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('MIDDLEWARE', value))
        SwaggerTesterSettings()


def test_excess_setting_middleware_setting(monkeypatch) -> None:
    with pytest.raises(
        ImproperlyConfigured,
        match='Received excess middleware setting, `EXTRA_SETTING`, for the RESPONSE_VALIDATION middleware settings. Please correct or remove this setting.',
    ):
        monkeypatch.setattr(
            django_settings, 'SWAGGER_TESTER', patch_response_validation_middleware_settings('EXTRA_SETTING', 'test')
        )
        SwaggerTesterSettings()
