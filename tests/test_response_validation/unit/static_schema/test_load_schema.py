import pytest
import yaml
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.static_schema.loader import LoadStaticSchema

yml_path = django_settings.BASE_DIR + '/demo_project/openapi-schema.yml'
json_path = django_settings.BASE_DIR + '/demo_project/openapi-schema.json'


def ret_schema(*args, **kwargs):
    with open(yml_path, 'r') as f:
        content = f.read()
    return yaml.load(content, Loader=yaml.FullLoader)


def ret_bad_schema(*args, **kwargs):
    schema = ret_schema()
    del schema['paths']['/api/v1/trucks/correct/']
    return schema


def test_successful_parse_documented_endpoints(monkeypatch) -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})
    monkeypatch.setattr('django_swagger_tester.static_schema.loader.LoadStaticSchema.get_schema', ret_schema)
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
        base = LoadStaticSchema(item['url'], 'get', status_code=200)  # type: ignore
        assert base.get_response_schema() == item['expected']


def test_successful_parse_undocumented_endpoints(monkeypatch) -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})
    monkeypatch.setattr('django_swagger_tester.static_schema.loader.LoadStaticSchema.get_schema', ret_schema)
    for url in ['/api/v1/cars/incorrect/', '/api/v1/trucks/incorrect/']:
        base = LoadStaticSchema(url, 'get', status_code=200)
        base.get_response_schema()


def test_method_missing_from_schema(monkeypatch) -> None:
    """
    Asserts that a non-existent method raises the appropriate exception.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})
    monkeypatch.setattr('django_swagger_tester.static_schema.loader.LoadStaticSchema.get_schema', ret_schema)
    with pytest.raises(
        ImproperlyConfigured,
        match='Method \`gets\` is invalid. Should be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.',
    ):
        LoadStaticSchema('api/v1/trucks/correct', 'gets', status_code=200)


def test_no_matching_routes(monkeypatch) -> None:
    """
    Asserts that the right exception is raised when an endpoint is not documented in the schema.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})
    monkeypatch.setattr('django_swagger_tester.static_schema.loader.LoadStaticSchema.get_schema', ret_bad_schema)
    with pytest.raises(ValueError, match='Could not resolve path'):
        LoadStaticSchema('apsi/v1/trucks/correct', 'get', status_code=200)
