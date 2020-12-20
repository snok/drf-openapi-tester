# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_response_validation_view_settings

from django_swagger_tester.configuration import SwaggerTesterSettings


def test_valid_debug(monkeypatch) -> None:
    """
    DEBUG must be a boolean.
    """
    for value in [True, False]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_response_validation_view_settings('DEBUG', value))
        SwaggerTesterSettings().validate()


def test_invalid_debug(monkeypatch) -> None:
    for value in ['test', None, {}, [], 2, 2.0]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_response_validation_view_settings('DEBUG', value))
        with pytest.raises(ImproperlyConfigured, match='DEBUG must be a boolean'):
            SwaggerTesterSettings().validate()
