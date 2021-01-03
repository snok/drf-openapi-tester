import pytest

from response_tester.exceptions import UndocumentedSchemaSectionError
from response_tester.openapi import index_schema, is_nullable
from tests.types import object_type

example = {
    'title': 'Other stuff',
    'description': 'the decorator should determine the serializer class for this',
    'required': ['foo'],
    'type': 'object',
    'properties': {'foo': {'title': 'Foo', 'type': 'string', 'minLength': 1}},
}

additional_example = {
    'title': 'Other stuff',
    'description': 'the decorator should determine the serializer class for this',
    'required': ['foo'],
    'type': 'object',
    'additionalProperties': {'title': 'Foo', 'type': 'string', 'minLength': 1},
}

nullable_example = {
    'properties': {
        'id': {
            'title': 'ID',
            'type': 'integer',
            'readOnly': 'true',
            'x-nullable': 'true',
        },
        'first_name': {
            'title': 'First name',
            'type': 'string',
            'maxLength': '30',
            'minLength': '1',
            'nullable': 'true',
        },
    }
}

nullable_example_data = {'id': None, 'first_name': None}


def test_is_nullable():
    """
    Ensure this helper function works as it's designed to.
    """
    assert is_nullable(nullable_example['properties']['id']) == True  # noqa: E712
    assert is_nullable(nullable_example['properties']['first_name']) == True  # noqa: E712
    for item in [2, '', None, -1, {'nullable': 'false'}]:
        assert is_nullable(item) is False


def test_index_schema():
    # Fail with no addon
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `items`'
    ):
        index_schema(schema=object_type, variable='items')

    # Fail with addon
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Unsuccessfully tried to index the OpenAPI schema by `items`. This is a very specific string',
    ):
        index_schema(schema=object_type, variable='items', error_addon='This is a very specific string')
