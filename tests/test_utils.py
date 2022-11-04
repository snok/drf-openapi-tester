import pytest

from openapi_tester.utils import is_path_an_url, merge_objects
from tests.utils import sort_object

object_1 = {"type": "object", "required": ["key1"], "properties": {"key1": {"type": "string"}}}
object_2 = {"type": "object", "required": ["key2"], "properties": {"key2": {"type": "string"}}}
merged_object = {
    "type": "object",
    "required": ["key1", "key2"],
    "properties": {"key1": {"type": "string"}, "key2": {"type": "string"}},
}


def test_documentation_error_sort_data_type():
    assert sort_object([1, 3, 2]) == [1, 2, 3]  # list
    assert sort_object({"1", "3", "2"}) == {"1", "2", "3"}  # set
    assert sort_object({"1": "a", "3": "a", "2": "a"}) == {"1": "a", "2": "a", "3": "a"}  # dict

    # Test sort failure scenario - expect the method to succeed and default to no reordering
    assert sort_object(["1", {}, []]) == ["1", {}, []]


def test_merge_objects():
    test_schemas = [
        object_1,
        object_2,
    ]
    expected = {
        "type": "object",
        "required": ["key1", "key2"],
        "properties": {"key1": {"type": "string"}, "key2": {"type": "string"}},
    }
    assert sort_object(merge_objects(test_schemas)) == sort_object(expected)


@pytest.mark.parametrize(
    ("path", "is_url"),
    [
        ("/path/to/schema", False),
        ("http://www.schema.com", True),
        ("https://www.schema.com", True),
        ("http://schemas:8000", True),
        ("http://schemas:8000/path/to/schema.yaml", True),
    ],
)
def test_is_path_an_url(path: str, is_url: bool):
    assert is_path_an_url(path) == is_url
