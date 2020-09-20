# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_response_validation_middleware_settings


def test_invalid_logger_name(monkeypatch):
    for value in [None, [], {}, (1, 2), 2, 2.0]:
        monkeypatch.setattr(
            django_settings, 'SWAGGER_TESTER', patch_response_validation_middleware_settings('LOGGER_NAME', value)
        )
        with pytest.raises(ImproperlyConfigured, match='Logger name must be a string'):
            SwaggerTesterSettings()
