# flake8: noqa
import pytest
from django.conf import settings

from openapi_tester.exceptions import ImproperlyConfigured
from openapi_tester.static.get_schema import fetch_from_dir
from openapi_tester.static.parse import parse_endpoint


def test_successful_parse() -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    schema = fetch_from_dir(settings.BASE_DIR + '/drf_yasg/openapi-schema.yml')
    for url in ['/api/v1/cars/correct/', '/api/v1/cars/incorrect/', '/api/v1/trucks/correct/', '/api/v1/trucks/incorrect/']:
        schema_section = parse_endpoint(schema, 'GET', url)
        assert schema_section == {'type': 'array', 'items': {}}


def test_bad_method() -> None:
    """
    Asserts that a bad method raises the appropriate exception.
    """
    with pytest.raises(ValueError, match='Method `GETS` is invalid. ' 'Should be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.'):
        schema_section = parse_endpoint('', 'GETS', '')


def test_bad_url() -> None:
    """
    Asserts that a bad url raises the appropriate exception.
    """
    with pytest.raises(ValueError, match='Could not resolve path ``'):
        schema_section = parse_endpoint('', 'GET', '')


def test_no_matching_routes() -> None:
    """
    Asserts that the right exception is raised when an endpoint is not documented in the schema.
    """
    schema = fetch_from_dir(settings.BASE_DIR + '/drf_yasg/openapi-schema.yml')
    del schema['paths']['/api/v1/trucks/correct/']
    with pytest.raises(ValueError, match='Could not match the resolved url to a documented endpoint in the OpenAPI specification'):
        schema_section = parse_endpoint(schema, 'GET', '/api/v1/trucks/correct/')


def test_no_matching_method() -> None:
    """
    Asserts that the right exception is raised when an endpoint is documented, but the particular method is not.
    """
    schema = fetch_from_dir(settings.BASE_DIR + '/drf_yasg/openapi-schema.yml')
    del schema['paths']['/api/v1/trucks/correct/']['get']
    with pytest.raises(KeyError, match='The OpenAPI schema has no method called `GET`'):
        schema_section = parse_endpoint(schema, 'GET', '/api/v1/trucks/correct/')
