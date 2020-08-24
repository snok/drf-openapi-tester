# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_middleware_settings


def test_non_bool_strict_setting(monkeypatch) -> None:
    """
    Make sure a non-boolean value is rejected.
    """
    for value in ['', 'test', None, {}, [], 2]:
        with pytest.raises(
            ImproperlyConfigured,
            match='The SWAGGER_TESTER middleware setting `REJECT_INVALID_REQUEST_BODIES` must be a boolean value',
        ):
            monkeypatch.setattr(
                django_settings, 'SWAGGER_TESTER', patch_middleware_settings('REJECT_INVALID_REQUEST_BODIES', value)
            )
            SwaggerTesterSettings()


def test_bool_strict_setting(monkeypatch) -> None:
    """
    Make sure all boolean values are accepted.
    """
    for value in [True, False]:
        monkeypatch.setattr(
            django_settings, 'SWAGGER_TESTER', patch_middleware_settings('REJECT_INVALID_REQUEST_BODIES', value)
        )
        SwaggerTesterSettings()
