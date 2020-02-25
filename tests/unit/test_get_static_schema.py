# flake8: noqa
import pytest
from django.conf import settings

from openapi_tester.exceptions import ImproperlyConfigured
from openapi_tester.static.get_schema import fetch_from_dir


def test_successful_yml_fetch() -> None:
    """
    Tests that a file is fetched successfully.
    """
    content = fetch_from_dir(settings.BASE_DIR + '/drf_yasg/openapi-schema.yml')
    assert 'openapi' in content


def test_successful_json_fetch() -> None:
    """
    Tests that a file is fetched successfully.
    """
    content = fetch_from_dir(settings.BASE_DIR + '/drf_yasg/openapi-schema.json')
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

            logger = logging.getLogger('openapi_tester')
            logger.exception('test')

    monkeypatch.setattr('openapi_tester.static.get_schema.logger', MockedLogger)

    with pytest.raises(
        ImproperlyConfigured, match='Could not read the openapi specification. Please make sure the path setting is correct.\n\nError: test'
    ):
        fetch_from_dir(settings.BASE_DIR + '/drf_yasg/openapi-schema.yml')