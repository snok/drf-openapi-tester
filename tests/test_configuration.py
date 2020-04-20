import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings


def test_valid_settings() -> None:
    """
    Assert that the default settings in the demo project pass without errors.
    """
    SwaggerTesterSettings()


def test_valid_cases(monkeypatch) -> None:  # noqa: TYP001
    """
    Assert that valid cases always pass without errors.
    """
    for case in [
        'snake case',
        'camel case',
        'pascal case',
        'kebab case',
        None,
        'snake_case',
        'camelCase',
        'PascalCase',
        'kebab-case',
    ]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'CASE': case})
        SwaggerTesterSettings()


def test_invalid_cases(monkeypatch) -> None:
    """
    Asserts that any invalid case raises an appropriate error.
    """
    for case in ['snakecase', 'camel', '', 1, -22, {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'CASE': case})
        with pytest.raises(
            ImproperlyConfigured,
            match=(
                'Set case to `snake case` for snake_case, `camel case` for '
                'camelCase, `pascal case` for PascalCase,`kebab case` for kebab-case, '
                'or to `None` to skip case validation outright.'
            ),
        ):
            SwaggerTesterSettings()


def test_empty_settings(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that no error is raised when empty SWAGGER_TESTER dict is specified.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {})
    SwaggerTesterSettings()


def test_missing_settings(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that no error is raised when no SWAGGER_TESTER dict is specified.
    """
    monkeypatch.delattr(django_settings, 'SWAGGER_TESTER')
    SwaggerTesterSettings()


def test_excess_settings(monkeypatch) -> None:  # noqa: TYP001
    """
    An error should be raised if an excess setting is specified.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'bad_setting': 5})
    with pytest.raises(ImproperlyConfigured, match='is not a valid setting for the django-swagger-tester module'):
        SwaggerTesterSettings()


def test_camel_case_parser_setting(monkeypatch) -> None:
    """
    Make sure all states are OK.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'CAMEL_CASE_PARSER': True})
    SwaggerTesterSettings()
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'CAMEL_CASE_PARSER': False})
    SwaggerTesterSettings()
    with pytest.raises(
        ImproperlyConfigured,
        match='\`CAMEL_CASE_PARSER\` needs to be True or False, or unspecified \(defaults to False\)',
    ):
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'CAMEL_CASE_PARSER': None})
        SwaggerTesterSettings()
