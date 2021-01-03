import pytest
from django.core.exceptions import ImproperlyConfigured

from openapi_tester.loaders import StaticSchemaLoader
from tests import json_path, yml_path


def test_successful_yml_fetch() -> None:
    """
    Tests that a file is fetched successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_path)
    content = base.get_schema()
    assert 'openapi' in content


def test_successful_json_fetch() -> None:
    """
    Tests that a file is fetched successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(json_path)
    content = base.get_schema()
    assert 'info' in content


def test_non_existent_file(caplog) -> None:
    """
    Asserts that a non-existent file will raise an error.
    """
    base = StaticSchemaLoader()
    base.set_path('test')
    with pytest.raises(
        ImproperlyConfigured,
        match='The path `test` does not point to a valid file. Make sure to point to the specification file.',
    ):
        base.get_schema()
        assert 'Path `test` does not resolve as a valid file.' in caplog.records


def test_unreadable_file(monkeypatch) -> None:
    """
    Asserts that the appropriate error is raised when we fail to read a file.
    """

    def mocked_isfile(*args, **kwargs):
        return True

    monkeypatch.setattr('response_tester.loaders.os.path.isfile', mocked_isfile)

    base = StaticSchemaLoader()
    base.set_path(yml_path + 's')
    with pytest.raises(
        ImproperlyConfigured, match='Unable to read the schema file. Please make sure the path setting is correct.'
    ):
        base.get_schema()


def test_bad_filetype() -> None:
    """
    Asserts that an appropriate exception is raised when a function tries to pass a non yml/json schema.
    """
    from django.conf import settings as django_settings

    base = StaticSchemaLoader()
    base.set_path(str(django_settings.BASE_DIR) + '/settings.py')  # must be a real file
    with pytest.raises(
        ImproperlyConfigured, match='The specified file path does not seem to point to a JSON or YAML file.'
    ):
        base.get_schema()
