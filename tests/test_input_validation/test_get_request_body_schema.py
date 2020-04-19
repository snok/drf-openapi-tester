import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.input_validation.utils import get_request_body_schema

example_schema = [
    {
        'name': 'data',
        'in': 'body',
        'required': True,
        'schema': {
            'required': ['vehicleType'],
            'type': 'object',
            'properties': {'vehicleType': {'title': 'Vehicle type', 'type': 'string', 'maxLength': 10, 'minLength': 1}},
            'example': {'vehicleType': 'truck'},
        },
    }
]

expected = {'vehicleType': 'truck'}


def test_json_conversion():
    """
    Test that the request body serializer converts an OpenAPI schema to JSON as it should.
    This is an area that might have to be expanded on in the future.
    """
    assert get_request_body_schema(example_schema)['example'] == expected


def test_error_handling():
    """
    If we get a schema we're not prepared for, we raise an error.
    """
    e = 'Input validation tries to test request body documentation, but the provided schema has no request body'
    with pytest.raises(ImproperlyConfigured, match=e):
        get_request_body_schema('test')
