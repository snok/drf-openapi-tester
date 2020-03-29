import pytest

from django_swagger_tester.dynamic.get_schema import fetch_generated_schema
from django_swagger_tester.exceptions import SwaggerDocumentationError


def test_dynamic_drf_yasg() -> None:
    """
    Asserts that the functions runs given correct inputs.
    """
    fetch_generated_schema(url='/cars/correct/', method='GET', status_code=200)


def test_bad_url() -> None:
    """
    Asserts that the right error message is raised when a bad URL is passed.
    """
    with pytest.raises(
        SwaggerDocumentationError,
        match='No path found for url `/cars/cor/`. Valid urls include /cars/correct/, '
        '/cars/incorrect/, /trucks/correct/, /trucks/incorrect/',
    ):
        fetch_generated_schema(url='/cars/cor/', method='GET', status_code=200)


def test_bad_method() -> None:
    """
    Asserts that the right error message is raised when a bad HTTP method is passed.
    """
    with pytest.raises(SwaggerDocumentationError, match='No schema found for method GETS. Available methods include GET, POST, PUT, DELETE.'):
        fetch_generated_schema(url='/cars/correct/', method='GETS', status_code=200)
