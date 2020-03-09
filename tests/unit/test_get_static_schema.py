# flake8: noqa
import pytest
from django.conf import settings

from django_swagger_tester.exceptions import ImproperlyConfigured
from django_swagger_tester.static.get_schema import fetch_from_dir


def test_successful_yml_fetch() -> None:
    """
    Tests that a file is fetched successfully.
    """
    content = fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.yml')
    assert 'openapi' in content


def test_successful_json_fetch() -> None:
    """
    Tests that a file is fetched successfully.
    """
    content = fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.json')
    assert 'title' in content


def test_non_existent_file(caplog) -> None:
    """
    Asserts that a non-existent file will raise an error.
    """
    with pytest.raises(
        ImproperlyConfigured, match='The path `test` does not point to a valid file. ' 'Make sure to point to the specification file.'
    ):
        fetch_from_dir('test')
        assert 'Path `test` does not resolve as a valid file.' in caplog.records


def test_unreadable_file(monkeypatch, caplog) -> None:
    """
    Asserts that the appropriate error is raised when we fail to read a file.
    """

    class MockedLogger:
        def debug(self, *args):
            raise Exception('test')

        def exception(self, *args):
            import logging

            logger = logging.getLogger('django_swagger_tester')
            logger.exception('test')

    monkeypatch.setattr('django_swagger_tester.static.get_schema.logger', MockedLogger)

    with pytest.raises(
        ImproperlyConfigured, match='Could not read the openapi specification. Please make sure the path setting is correct.\n\nError: test'
    ):
        fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.yml')


def test_bad_filetype() -> None:
    """
    Asserts that an appropriate exception is raised when a function tries to pass a non yml/json schema.
    """
    with pytest.raises(ImproperlyConfigured, match='The specified file path does not seem to point to a JSON or YAML file.'):
        fetch_from_dir(settings.BASE_DIR + '/demo_project/settings.py')
