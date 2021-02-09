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

Expected: {"key1": "string", "key2": "string", "key3": "string", "key4": [42]}

Received: {"key1": "test", "key2": "test", "key3": "test", "key4": [1, 2, 3]}

Hint: test:hint

Sequence: test:reference
"""
    assert error.args[0].strip() == expected.strip()


def test_case_error_message():
    error = CaseError(key="test-key", case="camelCase", expected="testKey")
    assert error.args[0].strip() == "The response key `test-key` is not properly camelCase. Expected value: testKey"
