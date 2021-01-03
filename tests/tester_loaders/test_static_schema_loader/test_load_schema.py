import pytest
from django.core.exceptions import ImproperlyConfigured

from response_tester.loaders import StaticSchemaLoader
from tests import yml_path
from tests.utils import ret_schema


def ret_bad_schema(*args, **kwargs):
    schema = ret_schema()
    del schema['paths']['/api/v1/trucks/correct/']
    return schema


def test_successful_parse_documented_endpoints(monkeypatch) -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_path)

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
                        'height': {
                            'description': 'How tall the truck is.',
                            'type': 'string',
                            'example': 'Medium height',
                        },
                        'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                        'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
                    },
                },
            },
        },
    ]
    for item in documented_endpoints:
        assert base.get_response_schema_section(route=item['url'], method='GET', status_code=200) == item['expected']


def test_successful_parse_undocumented_endpoints(monkeypatch) -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_path)
    for url in ['/api/v1/cars/incorrect/', '/api/v1/trucks/incorrect/']:
        base.get_response_schema_section(route=url, method='GET', status_code=200)


def test_method_missing_from_schema(monkeypatch) -> None:
    """
    Asserts that a non-existent method raises the appropriate exception.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_path)
    with pytest.raises(
        ImproperlyConfigured,
        match=r'Method \`gets\` is invalid. Should be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.',
    ):
        base.get_response_schema_section(route='api/v1/trucks/correct', method='gets', status_code=200)


def test_no_matching_routes(monkeypatch) -> None:
    """
    Asserts that the right exception is raised when an endpoint is not documented in the schema.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_path)
    with pytest.raises(ValueError, match='Could not resolve path'):
        base.get_response_schema_section(route='apsi/v1/trucks/correct', method='get', status_code=200)
