# noqa: TYP001
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_settings

from django_swagger_tester.case_testers import is_camel_case, is_kebab_case, is_pascal_case, is_snake_case
from django_swagger_tester.configuration import SwaggerTesterSettings


def test_valid_cases(monkeypatch) -> None:  # noqa: TYP001
    """
    Assert that valid cases always pass without errors.
    """
    for case in [
        is_snake_case,
        is_camel_case,
        is_pascal_case,
        is_kebab_case,
        lambda x: x * 2,  # custom callable
    ]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_TESTER', case))
        SwaggerTesterSettings()


def test_none(monkeypatch) -> None:
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_TESTER', None))
    with pytest.raises(
        ImproperlyConfigured,
        match=('The django-swagger-tester CASE_TESTER setting cannot be None. Replace it with `lambda: None`'),
    ):
        SwaggerTesterSettings()


def test_invalid_cases(monkeypatch) -> None:
    """
    Asserts that any invalid case raises an appropriate error.
    """
    for case in ['snakecase', 1, {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_TESTER', case))
        with pytest.raises(
            ImproperlyConfigured,
            match=(
                'The django-swagger-tester CASE_TESTER setting is misspecified. '
                'Please pass a case tester callable from django_swagger_tester.case_testers, '
                'make your own, or pass `None` to skip case validation.'
            ),
        ):
            SwaggerTesterSettings()


def test_valid_case_whitelist(monkeypatch) -> None:
    """
    The case whitelist should accept a list of strings or None (which defaults to an empty list)
    """
    for item, expected in [(['IP', 'DHCP'], ['IP', 'DHCP'])]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_PASSLIST', item))
        settings = SwaggerTesterSettings()
        assert settings.case_passlist == expected


def test_invalid_case_whitelist(monkeypatch) -> None:
    """
    The case whitelist validation should reject non-lists of strings
    """
    for item in [{'IP': None, 'DHCP': 2}, 2, -2, (None, [])]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_PASSLIST', item))
        with pytest.raises(ImproperlyConfigured, match='The CASE_PASSLIST setting needs to be a list of strings'):
            SwaggerTesterSettings()


def test_case_whitelist_contains_non_str(monkeypatch) -> None:
    """
    The case whitelist validation should reject non-lists of strings
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_PASSLIST', ['item', 2]))
    with pytest.raises(ImproperlyConfigured, match='The CASE_PASSLIST setting list can only contain strings'):
        SwaggerTesterSettings()
