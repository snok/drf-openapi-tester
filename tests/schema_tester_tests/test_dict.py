from copy import deepcopy

import pytest

from openapi_tester.exceptions import DocumentationError
from openapi_tester.loaders import BaseSchemaLoader
from openapi_tester.schema_tester import SchemaTester
from tests.utils import loader

schema = {
    'type': 'object',
    'properties': {
        'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
        'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
        'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
        'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
        'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
    },
}
data = {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}

tester = SchemaTester(
    schema={'type': 'array', 'items': {'type': 'object', 'properties': {}}},
    data=[],
    case_tester=None,
)


def test_valid_dict() -> None:
    """
    Asserts that valid data passes successfully.
    """
    tester.test_schema_section(schema=schema, data=data, reference='placeholder')


def test_nullable() -> None:
    """
    Asserts that valid data passes successfully.
    """
    schema = loader('/tests/drf_yasg_reference.yaml')
    base = BaseSchemaLoader()
    base.set_schema(schema)
    response_schema = base.schema['paths']['/articles/']['get']['responses']['200']['schema']
    data = {
        'count': 1,
        'next': None,
        'previous': 'nullable-string',
        'results': [
            {
                'title': 'string',
                'author': 1,
                'body': 'string',
                'slug': 'string',
                'date_created': 'datetime',
                'date_modified': 'datetime',
                'read_only_nullable': None,
                'references': {'': 'test'},
                'uuid': 'test',
                'cover': 'test',
                'cover_name': 'test',
                'article_type': None,  # can be 1
                'group': 'string',
                'original_group': 'string',
            }
        ],
    }

    # Test nullable values pass OK
    assert tester.test_schema_section(schema=response_schema, data=data, reference='placeholder') is None

    # Test nullable items do not pass if not documented as nullable
    d = deepcopy(data)
    with pytest.raises(
        DocumentationError,
        match='Mismatched types, expected int but received NoneType.',
    ):
        d['count'] = None
        tester.test_schema_section(schema=response_schema, data=d, reference='placeholder')

    # Test non-nullable dict does not pass OK
    with pytest.raises(
        DocumentationError,
        match='Mismatched types, expected dict but received NoneType.',
    ):
        data['results'] = [None]
        assert tester.test_schema_section(schema=response_schema, data=data, reference='placeholder') is None

    # Test nullable dict passes OK
    response_schema['properties']['results']['items']['x-nullable'] = True
    assert tester.test_schema_section(schema=response_schema, data=data, reference='placeholder') is None

    # Test non-nullable list does not pass OK
    with pytest.raises(
        DocumentationError,
        match='Mismatched types, expected list but received NoneType.',
    ):
        data['results'] = None
        assert tester.test_schema_section(schema=response_schema, data=data, reference='placeholder') is None

    # Test nullable list passes OK
    response_schema['properties']['results']['x-nullable'] = True
    assert tester.test_schema_section(schema=response_schema, data=data, reference='placeholder') is None


def test_bad_data_type() -> None:
    """
    Asserts that the appropriate exception is raised for a bad response data type.
    """
    with pytest.raises(
        DocumentationError,
        match='Mismatched types, expected dict but received list.',
    ):
        tester.test_schema_section(schema=schema, data=[data], reference='placeholder')


def test_unmatched_lengths() -> None:
    """
    Asserts that different dict lengths raises an exception.
    """
    with pytest.raises(
        DocumentationError,
        match='The following properties seem to be missing from your OpenAPI/Swagger documentation: `extra key`',
    ):
        weird_data = {'name': '', 'color': '', 'height': '', 'width': '', 'length': '', 'extra key': ''}
        tester.test_schema_section(schema=schema, data=weird_data, reference='placeholder')


def test_schema_key_not_in_response():
    """
    If the response and schema are the same length, but have different keys, an error should be raised.
    """
    bad_data = deepcopy(data)
    bad_data['names'] = bad_data['name']
    del bad_data['name']
    with pytest.raises(DocumentationError, match=r'Schema key `name` was not found in the test.'):
        tester.test_schema_section(schema=schema, data=bad_data, reference='placeholder')


def test_response_key_not_in_schema():
    """
    If the response and schema are the same length, but have different keys, an error should be raised.
    """
    bad_schema = deepcopy(schema)
    bad_schema['properties']['names'] = bad_schema['properties']['name']
    del bad_schema['properties']['name']
    with pytest.raises(DocumentationError, match=r'Key `name` not found in the OpenAPI schema.'):
        tester.test_schema_section(schema=bad_schema, data=data, reference='placeholder')


def test_call_dict_from_dict():
    """
    Verify that we're able to call the _dict method.
    """
    custom_schema = {'type': 'object', 'properties': {'test': schema}}
    custom_data = {'test': data}
    assert tester.test_schema_section(schema=custom_schema, data=custom_data, reference='placeholder') is None


def test_call_list_from_dict():
    """
    Verify that we're able to call the _list method.
    """
    custom_schema = {
        'type': 'object',
        'properties': {
            'list': {
                'type': 'array',
                'items': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
            }
        },
    }
    custom_data = {'list': []}
    assert tester.test_schema_section(schema=custom_schema, data=custom_data, reference='placeholder') is None
