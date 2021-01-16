import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from openapi_tester.configuration import OpenAPITesterSettings
from tests.utils import patch_settings


def test_valid_value(monkeypatch) -> None:
    """
    Make sure all states are OK.
    """
    monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', patch_settings('PARAMETERIZED_I18N_NAME', 'language'))
    OpenAPITesterSettings().validate()


def test_non_string_setting(monkeypatch) -> None:
    """
    A non-boolean value should raise an exception.
    """
    for x in [None, [], -2, True]:
        with pytest.raises(ImproperlyConfigured):
            monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', patch_settings('PARAMETERIZED_I18N_NAME', x))
            OpenAPITesterSettings().validate()
