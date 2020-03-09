# flake8: noqa
import pytest
from django.conf import settings

from django_swagger_tester.exceptions import ImproperlyConfigured
from django_swagger_tester.static.get_schema import fetch_from_dir
from django_swagger_tester.static.parse import parse_endpoint


def test_successful_parse_documented_endpoints() -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    schema = fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.yml')
    documented_endpoints = [
        {
            'url': '/api/v1/cars/correct/',
            'expected': {
                'title': 'Success',
                'type': 'array',
                'items': {
                    'title': 'Success',
                    'type': 'object',
                    'properties': {
                        'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
                        'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
                        'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
                        'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
                        'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
                    },
                },
            },
        },
        {
            'url': '/api/v1/trucks/correct/',
            'expected': {
                'title': 'Success',
                'type': 'array',
                'items': {
                    'title': 'Success',
                    'type': 'object',
                    'properties': {
                        'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                        'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                        'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                        'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                        'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
                    },
                },
            },
        },
    ]
    for item in documented_endpoints:
        print('s')
        schema_section = parse_endpoint(schema, 'GET', item['url'])
        assert schema_section == item['expected']


def test_successful_parse_undocumented_endpoints() -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    schema = fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.yml')

    for url in ['/api/v1/cars/incorrect/', '/api/v1/trucks/incorrect/']:
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
    schema = fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.yml')
    del schema['paths']['/api/v1/trucks/correct/']
    with pytest.raises(ValueError, match='Could not match the resolved url to a documented endpoint in the OpenAPI specification'):
        schema_section = parse_endpoint(schema, 'GET', '/api/v1/trucks/correct/')


def test_no_matching_method() -> None:
    """
    Asserts that the right exception is raised when an endpoint is documented, but the particular method is not.
    """
    schema = fetch_from_dir(settings.BASE_DIR + '/demo_project/openapi-schema.yml')
    del schema['paths']['/api/v1/trucks/correct/']['get']
    with pytest.raises(KeyError, match='The OpenAPI schema has no method called `GET`'):
        schema_section = parse_endpoint(schema, 'GET', '/api/v1/trucks/correct/')
