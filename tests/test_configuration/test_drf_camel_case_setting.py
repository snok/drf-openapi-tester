# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_settings

from django_swagger_tester.configuration import SwaggerTesterSettings


def test_enable_camel_case(monkeypatch) -> None:
    """
    Make sure all states are OK.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CAMEL_CASE_PARSER', True))
    SwaggerTesterSettings().validate()


def test_disable_camel_case(monkeypatch, caplog) -> None:
    """
    Make sure a warning log is output if CAMEL_CASE_PARSER is False, but the parser is found in the Django DRF settings.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CAMEL_CASE_PARSER', False))
    SwaggerTesterSettings().validate()
    assert (
        'Found `djangorestframework_camel_case` in REST_FRAMEWORK settings, but CAMEL_CASE_PARSER is not set to True'
        in caplog.text
    )


def test_missing_camel_case_parser_setting(monkeypatch) -> None:
    """
    A non-boolean value should raise an exception.
    """
    with pytest.raises(ImproperlyConfigured, match='`CAMEL_CASE_PARSER` needs to be True or False'):
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CAMEL_CASE_PARSER', None))
        SwaggerTesterSettings().validate()


def test_djangorestframework_camel_case_not_installed():
    """
    Verify that validation raises an exception if the package isnt installed.
    """
    import sys

    # Mock away the dependency
    temp = sys.modules['djangorestframework_camel_case']
    sys.modules['djangorestframework_camel_case'] = None

    e = 'The package `djangorestframework_camel_case` is not installed, and is required to enable camel case parsing.'
    with pytest.raises(ImproperlyConfigured, match=e):
        SwaggerTesterSettings().validate()

    sys.modules['djangorestframework_camel_case'] = temp
