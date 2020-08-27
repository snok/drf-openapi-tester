# noqa: TYP001
from copy import deepcopy

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


def test_true_while_validate_request_bodies_is_false(monkeypatch) -> None:
    """
    If an app has set VALIDATE_REQUEST_BODY to False, and the reject-setting to True, an error should be raised to
    notify the user (because it makes no sense).
    """
    default_settings = deepcopy(django_settings.SWAGGER_TESTER)
    default_middleware_settings = default_settings['MIDDLEWARE']
    patched_middleware_settings = default_middleware_settings
    patched_middleware_settings['REJECT_INVALID_REQUEST_BODIES'] = True
    patched_middleware_settings['VALIDATE_REQUEST_BODY'] = False
    default_settings['MIDDLEWARE'] = patched_middleware_settings
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', default_settings)
    with pytest.raises(
        ImproperlyConfigured,
        match='REJECT_INVALID_REQUEST_BODIES middleware setting cannot be True if VALIDATE_REQUEST_BODY is False.',
    ):
        SwaggerTesterSettings()
