import pytest

from response_tester.exceptions import DocumentationError
from response_tester.schema_tester import SchemaTester

base = SchemaTester({"type": "array", "items": {}}, [], lambda x, y: None, origin="test")

items = [
    {
        "schema": {"description": "This is a description for a float", "type": "number", "example": 2.1},
        "good_data": 5.0,
        "bad_data": 5,
    },
    {
        "schema": {"description": "This is a description for a file", "type": "file", "example": "image/jpeg"},
        "good_data": "string",
        "bad_data": 5,
    },
    {
        "schema": {"description": "This is a description for a bool", "type": "boolean", "example": "true"},
        "good_data": True,
        "bad_data": 5,
    },
    {
        "schema": {"description": "This is a description for a string", "type": "string", "example": "test"},
        "good_data": "string",
        "bad_data": 5,
    },
    {
        "schema": {"description": "This is a description for an integer", "type": "integer", "example": 2},
        "good_data": 1,
        "bad_data": "1",
    },
]


def test_valid_item_types():
    """
    Verify that all valid item types pass successfully.
    """
    for item in items:
        base.test_item(schema=item["schema"], data=item["good_data"], reference="test")


def test_invalid_item_types():
    """
    Verify that all invalid item types raise appropriate exceptions.
    """
    for item in items:
        with pytest.raises(DocumentationError):
            base.test_item(schema=item["schema"], data=item["bad_data"], reference="placeholder")
