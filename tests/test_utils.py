from openapi_tester.utils import combine_sub_schemas, merge_objects
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


def test_combine_sub_schemas_array_list():
    test_schemas = [{"type": "array", "items": {"type": "string"}}, {"type": "array", "items": {"type": "integer"}}]
    expected = {"type": "array", "items": {"type": "string"}}
    assert sort_object(combine_sub_schemas(test_schemas)) == sort_object(expected)


def test_combine_sub_schemas_object_list():
    test_schemas = [object_1, object_2]
    assert sort_object(combine_sub_schemas(test_schemas)) == sort_object({**merged_object})


def test_merge_objects():
    test_schemas = [
        object_1,
        object_2,
        {"type": "object", "properties": {"key3": {"allOf": [object_1, object_2]}}},
    ]
    expected = {
        "type": "object",
        "required": ["key1", "key2"],
        "properties": {"key1": {"type": "string"}, "key2": {"type": "string"}, "key3": merged_object},
    }
    assert sort_object(merge_objects(test_schemas)) == sort_object(expected)
