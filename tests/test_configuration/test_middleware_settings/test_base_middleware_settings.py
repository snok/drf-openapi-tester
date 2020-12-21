# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_response_validation_middleware_settings, patch_settings

from django_swagger_tester.configuration import SwaggerTesterSettings


def test_missing_middleware_settings(monkeypatch) -> None:
    """
    Assert that passing None or {} as middleware settings doesn't cause errors.
    """
    for value in [None, {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('MIDDLEWARE', value))
        SwaggerTesterSettings().validate()
