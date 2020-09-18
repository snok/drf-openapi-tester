# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_response_validation_middleware_settings


def test_bad_regular_expressions(monkeypatch) -> None:
    """
    Make sure values are rejected when they cannot be compiled using re.compile.
    """
    for value in [None, 2]:
        with pytest.raises(
            ImproperlyConfigured, match='Failed to compile the passed VALIDATION_EXEMPT_URLS as regular expressions'
        ):
            monkeypatch.setattr(
                django_settings,
                'SWAGGER_TESTER',
                patch_response_validation_middleware_settings('VALIDATION_EXEMPT_URLS', value),
            )
            SwaggerTesterSettings()


def test_accepted_regexp(monkeypatch) -> None:
    """
    Make sure normal regular expressions pass.
    """
    for value in ['^api/v1/test$', '']:
        monkeypatch.setattr(
            django_settings, 'SWAGGER_TESTER', patch_response_validation_middleware_settings('VALIDATION_EXEMPT_URLS', value)
        )
        SwaggerTesterSettings()
