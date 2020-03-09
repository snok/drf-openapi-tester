import os

import pytest
from django.conf import settings as django_settings

from django_swagger_tester.configuration import load_settings
from django_swagger_tester.exceptions import ImproperlyConfigured


def test_valid_settings() -> None:
    """
    Assert that the default settings in the demo project pass without errors.
    """
    load_settings()


def test_valid_cases(monkeypatch) -> None:  # noqa: TYP001
    """
    Assert that valid cases always pass without errors.
    """
    for case in ['snake case', 'camel case', 'pascal case', 'kebab case', None]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'SCHEMA': 'dynamic', 'CASE': case})
        load_settings()


def test_missing_settings(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that an error is raised when no SWAGGER_TESTER dict is specified.
    -> empty dict is fine, because all values have defaults.
    """
    monkeypatch.delattr(django_settings, 'SWAGGER_TESTER')
    with pytest.raises(ImproperlyConfigured, match='Please specify SWAGGER_TESTER settings in your settings.py'):
        load_settings()


def test_empty_settings(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that no error is raised when empty SWAGGER_TESTER dict is specified.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {})
    load_settings()


def test_missing_path(monkeypatch) -> None:  # noqa: TYP001
    """
    Test that a path is required when the schema type is `static`
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'SCHEMA': 'static'})
    with pytest.raises(
        ImproperlyConfigured,
        match='`PATH` is a required setting for the openapi-tester module. ' 'Please update your SWAGGER_TESTER settings.',
    ):
        load_settings()


def test_bad_path(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that an incorrect path type raises an exception.
    """
    for item in [2, -2, 2.2, [], (1,), {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'SCHEMA': 'static', 'CASE': None, 'PATH': item})
        with pytest.raises(ImproperlyConfigured, match='`PATH` needs to be a string. Please update your SWAGGER_TESTER settings.'):
            load_settings()


def test_invalid_setting(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that an incorrect settings dict raises an exception.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'test': 'test'})
    with pytest.raises(ImproperlyConfigured, match='`test` is not a valid setting for the openapi-tester module'):
        load_settings()


def test_invalid_cases(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that an incorrect CASE setting raises as exception.
    """
    for case in ['snakecase', 'camel', '', 1, -22, {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'SCHEMA': 'dynamic', 'CASE': case})
        with pytest.raises(
            ImproperlyConfigured,
            match=f'The openapi-tester package currently doesn\'t support a case called {case}.'
        ):
            load_settings()


def test_invalid_paths(monkeypatch, caplog) -> None:  # noqa: TYP001
    """
    Asserts that a string PATH setting, that doesn't point to a real file raises as exception.
    """
    for path in ['', '.', 'www.google.com']:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': path, 'SCHEMA': 'static'})
        with pytest.raises(ImproperlyConfigured):
            load_settings()
            assert f'Path {path} does not resolve as a valid file.' in caplog.messages


def test_invalid_file_type(monkeypatch, caplog) -> None:  # noqa: TYP001
    """
    Asserts that a string PATH setting that points to a real file, but of the wrong file type raises as exception.
    """
    path = os.path.abspath(os.path.join(django_settings.BASE_DIR, '..', '..', 'README.rst'))
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': path, 'SCHEMA': 'static'})
    with pytest.raises(ImproperlyConfigured):
        load_settings()
        assert f'Path does not include a file type, e.g., `.json` or `.yml`' in caplog.messages


def test_bad_schema(monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that an incorrect SCHEMA setting raises as exception.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'SCHEMA': None})
    with pytest.raises(
        ImproperlyConfigured,
        match=f'`SCHEMA` needs to be set to `dynamic` or `static` in the openapi-tester module, not None',
    ):
        load_settings()
