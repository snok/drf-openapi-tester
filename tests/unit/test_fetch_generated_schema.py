import pytest

from openapi_tester.dynamic.get_schema import fetch_generated_schema


def test_dynamic_drf_yasg() -> None:
    """
    Asserts that the functions runs given correct inputs.
    """
    fetch_generated_schema(url='/cars/correct/', status_code=200, method='GET')
    fetch_generated_schema(url='/cars/correct/', status_code='200', method='GET')


def test_bad_url() -> None:
    """
    Asserts that the right error message is raised when a bad URL is passed.
    """
    with pytest.raises(
        KeyError,
        match='No path found for url `/cars/cor/`. Valid urls include /cars/correct/, '
        '/cars/incorrect/, /trucks/correct/, /trucks/incorrect/',
    ):
        fetch_generated_schema(url='/cars/cor/', status_code=200, method='GET')


def test_bad_method() -> None:
    """
    Asserts that the right error message is raised when a bad HTTP method is passed.
    """
    with pytest.raises(KeyError, match='No schema found for method GETS. Available methods include GET, POST, PUT, DELETE.'):
        fetch_generated_schema(url='/cars/correct/', status_code=200, method='GETS')


def test_bad_status_code() -> None:
    """
    Asserts that the right error message is raised when a bad status code is passed.
    """
    with pytest.raises(KeyError, match='No schema found for response code 201. Documented responses include 200, 400, 401, 500.'):
        fetch_generated_schema(url='/cars/correct/', status_code=201, method='GET')
