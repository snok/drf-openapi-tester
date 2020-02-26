import pytest

from openapi_tester.case_checks import is_camel_case
from openapi_tester.exceptions import SpecificationError
from openapi_tester.tester import _dict

schema = {
    'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
    'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
    'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
    'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
    'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
}
data = {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}


def test_valid_dict() -> None:
    """
    Asserts that valid data passes successfully.
    """
    _dict(schema=schema, data=data, case_func=is_camel_case)


def test_bad_data_type() -> None:
    """
    Asserts that the appropriate exception is raised for a bad response data type.
    """
    with pytest.raises(SpecificationError, match="The response is <class 'list'> where it should be <class 'dict'>"):
        _dict(schema=schema, data=[data], case_func=is_camel_case)


def test_unmatched_lengths() -> None:
    """
    Asserts that different dict lengths raises an exception.
    """
    data = {'name': '', 'color': '', 'height': '', 'width': '', 'length': '', 'extra key': ''}
    with pytest.raises(
        SpecificationError, match='The following properties seem to be missing from your OpenAPI/Swagger documentation: `extra key`'
    ):
        _dict(schema=schema, data=data, case_func=is_camel_case)
