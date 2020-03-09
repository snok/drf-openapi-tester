import pytest

from django_swagger_tester.case_checks import is_camel_case
from django_swagger_tester.exceptions import OpenAPISchemaError
from django_swagger_tester.validate_response import _list

schema = {
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
}
data = [
    {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
    {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
    {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
]


def test_valid_list() -> None:
    """
    Asserts that valid data passes successfully.
    """
    _list(schema=schema, data=data, case_func=is_camel_case)


def test_bad_data_type() -> None:
    """
    Asserts that the appropriate exception is raised for a bad response data type.
    """
    with pytest.raises(OpenAPISchemaError, match="The response is <class 'dict'> when it should be <class 'list'>"):
        _list(schema=schema, data={'test': data}, case_func=is_camel_case)


def test_empty_response_data_list() -> None:
    """
    Asserts that the no exception is raised when the response data is missing - this has valid cases.
    """
    _list(schema=schema, data=[], case_func=is_camel_case)
