from openapi_tester.utils import combine_sub_schemas, sort_object


def test_documentation_error_sort_data_type():
    assert sort_object([1, 3, 2]) == [1, 2, 3]  # list
    assert sort_object({"1", "3", "2"}) == {"1", "2", "3"}  # set
    assert sort_object({"1": "a", "3": "a", "2": "a"}) == {"1": "a", "2": "a", "3": "a"}  # dict

    # Test sort failure scenario - expect the method to succeed and default to no reordering
    assert sort_object(["1", {}, []]) == ["1", {}, []]


def test_combine_sub_schemas_array_list():
    test_schemas = [{"type": "array", "items": {"type": "string"}}, {"type": "array", "items": {"type": "integer"}}]
    expected = {"type": "array", "items": {"type": "integer"}}
    assert sort_object(combine_sub_schemas(test_schemas)) == sort_object(expected)


def test_combine_sub_schemas_object_list():
    test_schemas = [
        {"type": "object", "required": ["key1"], "properties": {"key1": {"type": "string"}}},
        {"type": "object", "required": ["key2"], "properties": {"key2": {"type": "string"}}},
    ]
    expected = {
        "type": "object",
        "required": ["key1", "key2"],
        "properties": {"key1": {"type": "string"}, "key2": {"type": "string"}},
    }
    assert sort_object(combine_sub_schemas(test_schemas)) == sort_object(expected)
