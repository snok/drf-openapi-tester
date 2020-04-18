# flake8: noqa

import pytest
from django.conf import settings, settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.static_schema.loader import LoadStaticSchema

yml_path = django_settings.BASE_DIR + '/demo_project/openapi-schema.yml'
json_path = django_settings.BASE_DIR + '/demo_project/openapi-schema.json'


def test_successful_yml_fetch(monkeypatch) -> None:
    """
    Tests that a file is fetched successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})
    base = LoadStaticSchema('api/v1/trucks/correct', 'GET', status_code=200)
    content = base.get_schema()
    assert 'openapi' in content


def test_successful_json_fetch(monkeypatch) -> None:
    """
    Tests that a file is fetched successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': json_path})
    base = LoadStaticSchema('api/v1/trucks/correct', 'GET', status_code=200)
    content = base.get_schema()
    assert 'title' in content


def test_non_existent_file(caplog, monkeypatch) -> None:
    """
    Asserts that a non-existent file will raise an error.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': 'test'})
    base = LoadStaticSchema('api/v1/trucks/correct', 'GET', status_code=200)
    with pytest.raises(
        ImproperlyConfigured,
        match='The path `test` does not point to a valid file. Make sure to point to the specification file.',
    ):
        base.get_schema()
        assert 'Path `test` does not resolve as a valid file.' in caplog.records


def test_unreadable_file(monkeypatch, caplog) -> None:
    """
    Asserts that the appropriate error is raised when we fail to read a file.
    """

    def mocked_isfile(*args, **kwargs):
        return True

    monkeypatch.setattr('django_swagger_tester.static_schema.loader.os.path.isfile', mocked_isfile)

    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path + 's'})
    base = LoadStaticSchema('api/v1/trucks/correct', 'GET', status_code=200)
    with pytest.raises(
        ImproperlyConfigured, match='Unable to read the schema file. Please make sure the path setting is correct.'
    ):
        base.get_schema()


def test_bad_filetype(monkeypatch) -> None:
    """
    Asserts that an appropriate exception is raised when a function tries to pass a non yml/json schema.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': settings.BASE_DIR + '/demo_project/settings.py'})
    base = LoadStaticSchema('api/v1/trucks/correct', 'GET', status_code=200)
    with pytest.raises(
        ImproperlyConfigured, match='The specified file path does not seem to point to a JSON or YAML file.'
    ):
        base.get_schema()
