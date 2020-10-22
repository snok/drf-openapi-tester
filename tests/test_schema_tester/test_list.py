import pytest
from tests.types import (
    bool_data,
    bool_type,
    integer_data,
    integer_type,
    list_data,
    list_type,
    number_data,
    number_type,
    string_data,
    string_type,
)

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.schema_tester import SchemaTester

tester = SchemaTester({'type': 'array', 'items': {}}, [], lambda x, y: None, origin='test')


def test_valid_list() -> None:
    """
    Asserts that valid data passes successfully.
    """
    tester.test_list(schema=list_type, data=list_data, reference='placeholder')


def test_bad_data_type() -> None:
    """
    Asserts that the appropriate exception is raised for a bad response data type.
    """
    with pytest.raises(SwaggerDocumentationError, match="Expected item to be <class 'list'> but found <class 'dict'>"):
        tester.test_list(schema=list_type, data={'test': list_data}, reference='placeholder')


def test_empty_schema_list() -> None:
    with pytest.raises(
        SwaggerDocumentationError, match='Mismatched content. Response array contains data, when schema is empty.'
    ):
        l = {'title': 'list_type_title', 'type': 'array', 'items': {}}  # empty list
        tester.test_list(schema=l, data=list_data, reference='placeholder')


def test_empty_response_data_list() -> None:
    """
    Asserts that the no exception is raised when the response data is missing - this has valid cases.
    """
    tester.test_list(schema=list_type, data=[], reference='placeholder')


def test_call_list_from_list():
    """
    Verify that we're able to call _list from _list successfully.
    """
    custom_list = {
        'title': 'list_type_title',
        'type': 'array',
        'items': {
            'title': 'list_type_title',
            'type': 'array',
            'items': {
                'title': 'object_type_title',
                'type': 'object',
                'properties': {
                    'string': string_type,
                    'integer': integer_type,
                    'number': number_type,
                    'bool': bool_type,
                },
            },
        },
    }
    custom_data = [[{'string': string_data, 'integer': integer_data, 'number': number_data, 'bool': bool_data}]]
    assert tester.test_list(schema=custom_list, data=custom_data, reference='placeholder') is None


def test_call_item_from_list():
    """
    Verify that we're able to call _list from _list successfully.
    """
    for type_schema in [
        (string_type, string_data),
        (bool_type, bool_data),
        (number_type, number_data),
        (integer_type, integer_data),
    ]:
        custom_list = {'title': 'list_type_title', 'type': 'array', 'items': type_schema[0]}
        custom_data = [type_schema[1]]
        assert tester.test_list(schema=custom_list, data=custom_data, reference='placeholder') is None


def test_bad_type():
    """
    If a schema is passed, with unsupported types, we want to raise a general exception.
    """
    custom_schema = {
        'type': 'array',
        'items': {'description': 'How long the car is.', 'type': 'stringo', 'example': '2 meters'},
    }
    custom_data = ['test']
    with pytest.raises(
        Exception, match='Schema item has an invalid `type` attribute. The type `stringo` is not supported.'
    ):
        assert tester.test_list(schema=custom_schema, data=custom_data, reference='placeholder') is None
