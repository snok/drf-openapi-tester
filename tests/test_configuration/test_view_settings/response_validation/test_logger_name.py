# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_response_validation_view_settings

from django_swagger_tester.configuration import SwaggerTesterSettings


def test_invalid_logger_name(monkeypatch):
    for value in [None, [], {}, (1, 2), 2, 2.0]:
        monkeypatch.setattr(
            django_settings, 'SWAGGER_TESTER', patch_response_validation_view_settings('LOGGER_NAME', value)
        )
        with pytest.raises(ImproperlyConfigured, match='Logger name must be a string'):
            SwaggerTesterSettings().validate()
