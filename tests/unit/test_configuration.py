import os

import pytest
from django.conf import settings as django_settings

from openapi_tester.exceptions import ImproperlyConfigured
from openapi_tester.configuration import load_settings

# TODO: Expand test suite to cover new settings (schema)


def test_valid_settings():
    load_settings()


def test_valid_cases(monkeypatch):
    for case in ['snake case', 'camel case', 'pascal case', 'kebab case', None]:
        monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'SCHEMA': 'dynamic', 'CASE': case})
        load_settings()


def test_valid_paths(monkeypatch):
    with open(django_settings.BASE_DIR + '/openapitestertest.json', 'w+') as f:
        f.write('{}')
    with open(django_settings.BASE_DIR + '/openapitestertest.yaml', 'w+') as f:
        f.write('{}')
    with open(django_settings.BASE_DIR + '/openapitestertest.yml', 'w+') as f:
        f.write('{}')
    for path in [
        f'{django_settings.BASE_DIR + "test.json"}',
        f'{django_settings.BASE_DIR + "test.yaml"}',
        f'{django_settings.BASE_DIR + "test.yml"}',
    ]:
        monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'SCHEMA': 'static', 'PATH': path, 'CASE': None})
        load_settings()
    os.remove(django_settings.BASE_DIR + '/openapitestertest.json')
    os.remove(django_settings.BASE_DIR + '/openapitestertest.yaml')
    os.remove(django_settings.BASE_DIR + '/openapitestertest.yml')


def test_missing_settings(monkeypatch):
    monkeypatch.delattr(django_settings, 'OPENAPI_TESTER')
    with pytest.raises(ImproperlyConfigured, match='Please specify OPENAPI_TESTER in your settings.py'):
        load_settings()


def test_missing_path(monkeypatch):
    monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'CASE': None})
    load_settings()


def test_bad_path(monkeypatch):
    for item in [2, -2, 2.2, [], (1,), {}]:
        monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'SCHEMA': 'static', 'CASE': None, 'PATH': 2})
        with pytest.raises(ImproperlyConfigured, match='`PATH` needs to be a string. Please update your OPENAPI_TESTER settings.'):
            load_settings()


def test_invalid_setting(monkeypatch):
    monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'test': 'test'})
    with pytest.raises(ImproperlyConfigured, match='`test` is not a valid setting for the openapi-tester module'):
        load_settings()


def test_invalid_cases(monkeypatch):
    for case in ['snakecase', 'camel', '', 1, -22, {}]:
        monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'SCHEMA': 'dynamic', 'CASE': case})
        with pytest.raises(
            ImproperlyConfigured,
            match=(
                f'The openapi-tester package currently doesn\'t support a case called {case}.'
                f' Set case to `snake case` for snake_case, '
                f'`camel case` for camelCase, '
                f'`pascal case` for PascalCase,'
                f'`kebab case` for kebab-case, or None to skip case validation completely.'
            ),
        ):
            load_settings()


def test_invalid_paths(monkeypatch):
    for path in ['', None, 1, '.', 'www.google.com', f'{django_settings.BASE_DIR + "/README.rst"}']:
        monkeypatch.setattr(django_settings, 'OPENAPI_TESTER', {'path': path, 'case': None})
        with pytest.raises(ImproperlyConfigured):
            load_settings()
