from openapi_tester.exceptions import CaseError, DocumentationError


def test_documentation_error_message():
    error = DocumentationError(
        message="Test error message",
        response={"key3": "test", "key2": "test", "key1": "test", "key4": [1, 2, 3]},
        schema={
            "title": "object_type_title",
            "type": "object",
            "properties": {
                "key2": {
                    "description": "This is a string type",
                    "type": "string",
                },
                "key3": {
                    "description": "This is a string type",
                    "type": "string",
                },
                "key1": {
                    "description": "This is a string type",
                    "type": "string",
                },
                "key4": {"type": "array", "items": {"type": "integer"}},
            },
        },
        reference="test:reference",
        hint="test:hint",
    )

    expected = """
Error: Test error message

Expected: {"key1": "str", "key2": "str", "key3": "str", "key4": ["int"]}

Received: {"key1": "test", "key2": "test", "key3": "test", "key4": [1, 2, 3]}

Hint: test:hint

Sequence: test:reference
"""
    assert error.args[0].strip() == expected.strip()


def test_case_error_message():
    error = CaseError(key="test-key", case="camelCase", expected="testKey")
    assert error.args[0].strip() == "The response key `test-key` is not properly camelCase. Expected value: testKey"


def test_documentation_error_sort_data_type():
    assert DocumentationError._sort_data([1, 3, 2]) == [1, 2, 3]  # list
    assert DocumentationError._sort_data({"1", "3", "2"}) == {"1", "2", "3"}  # set
    assert DocumentationError._sort_data({"1": "a", "3": "a", "2": "a"}) == {"1": "a", "2": "a", "3": "a"}  # dict

    # Test sort failure scenario - expect the method to succeed and default to no reordering
    assert DocumentationError._sort_data(["1", {}, []]) == ["1", {}, []]
