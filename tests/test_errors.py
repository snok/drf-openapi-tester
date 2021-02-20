import pytest

from openapi_tester import SchemaTester
from openapi_tester.exceptions import CaseError, DocumentationError
from openapi_tester.validators import (
    validate_enum,
    validate_format,
    validate_max_items,
    validate_max_length,
    validate_max_properties,
    validate_maximum,
    validate_min_items,
    validate_min_length,
    validate_min_properties,
    validate_minimum,
    validate_multiple_of,
    validate_pattern,
    validate_type,
    validate_unique_items,
)


def test_case_error_message():
    error = CaseError(key="test-key", case="camelCase", expected="testKey")
    assert error.args[0].strip() == "The response key `test-key` is not properly camelCase. Expected value: testKey"


class TestValidatorErrors:

    # Message only-format exceptions

    def test_validate_min_properties_error(self):
        message = validate_min_properties({"minProperties": 2}, {})
        assert message == "The number of properties in {} is fewer than the specified minimum number of properties of 2"

    def test_validate_max_properties_error(self):
        message = validate_max_properties({"maxProperties": 1}, {"one": 1, "two": 2})
        assert (
            message == "The number of properties in {'one': 1, 'two': 2} exceeds the"
            " specified maximum number of properties of 1"
        )

    def test_validate_max_items_error(self):
        message = validate_max_items({"maxItems": 1}, [1, 2])
        assert message == "The length of the array [1, 2] exceeds the specified maximum length of 1"

    def test_validate_min_items_error(self):
        message = validate_min_items({"minItems": 1}, [])
        assert message == "The length of the array [] is shorter than the specified minimum length of 1"

    def test_validate_max_length_error(self):
        message = validate_max_length({"maxLength": 1}, "test")
        assert message == 'The length of "test" exceeds the specified maximum length of 1'

    def test_validate_min_length_error(self):
        message = validate_min_length({"minLength": 5}, "test")
        assert message == 'The length of "test" is shorter than the specified minimum length of 5'

    def test_validate_unique_items_error(self):
        message = validate_unique_items({"uniqueItems": True}, [1, 2, 1])
        assert message == "The array [1, 2, 1] must contain unique items only"

    def test_validate_minimum_error(self):
        message = validate_minimum({"minimum": 2}, 0)
        assert message == "The response value 0 is lower than the specified minimum of 2"

    def test_validate_exclusive_minimum_error(self):
        message = validate_minimum({"minimum": 2, "exclusiveMinimum": True}, 2)
        assert message == "The response value 2 is lower than the specified minimum of 3"

        message = validate_minimum({"minimum": 2, "exclusiveMinimum": False}, 2)
        assert message is None

    def test_validate_maximum_error(self):
        message = validate_maximum({"maximum": 2}, 3)
        assert message == "The response value 3 exceeds the maximum allowed value of 2"

    def test_validate_exclusive_maximum_error(self):
        message = validate_maximum({"maximum": 2, "exclusiveMaximum": True}, 2)
        assert message == "The response value 2 exceeds the maximum allowed value of 1"

        message = validate_maximum({"maximum": 2, "exclusiveMaximum": False}, 2)
        assert message is None

    def test_validate_multiple_of_error(self):
        message = validate_multiple_of({"multipleOf": 2}, 3)
        assert message == "The response value 3 should be a multiple of 2"

    def test_validate_pattern_error(self):
        message = validate_pattern({"pattern": "^[a-z]$"}, "3")
        assert message == 'The string "3" does not match the specified pattern: ^[a-z]$'

    # Formatted errors

    def test_validate_enum_error(self):
        message = validate_enum({"enum": ["Cat"]}, "Turtle")
        assert message == "Expected: a member of the enum ['Cat']\n\nReceived: \"Turtle\""

    def test_validate_format_error(self):
        d = [
            ({"format": "byte"}, "not byte"),
            ({"format": "base64"}, "not byte"),
            ({"format": "date"}, "not date"),
            ({"format": "date-time"}, "not date-time"),
            ({"format": "double"}, "not double"),
            ({"format": "email"}, "not email"),
            ({"format": "float"}, "not float"),
            ({"format": "ipv4"}, "not ipv4"),
            ({"format": "ipv6"}, "not ipv6"),
            ({"format": "time"}, "not time"),
            ({"format": "uri"}, "not uri"),
            ({"format": "url"}, "not url"),
        ]
        for (schema, data) in d:
            message = validate_format(schema, data)
            assert message == f'''Expected: a "{schema['format']}" formatted value\n\nReceived: "{data}"'''

    def test_validate_type_error(self):
        # string
        message = validate_type({"type": "string"}, 1)
        assert message == 'Expected: a "string" type value\n\nReceived: 1'

        # file
        message = validate_type({"type": "file"}, 1)
        assert message == 'Expected: a "file" type value\n\nReceived: 1'

        # boolean
        message = validate_type({"type": "boolean"}, 1)
        assert message == 'Expected: a "boolean" type value\n\nReceived: 1'

        # integer
        message = validate_type({"type": "integer"}, True)
        assert message == 'Expected: an "integer" type value\n\nReceived: True'

        # number
        message = validate_type({"type": "number"}, "string")
        assert message == 'Expected: a "number" type value\n\nReceived: "string"'

        # number
        message = validate_type({"type": "number"}, "string")
        assert message == 'Expected: a "number" type value\n\nReceived: "string"'

        # object
        message = validate_type({"type": "object"}, "string")
        assert message == 'Expected: an "object" type value\n\nReceived: "string"'

        # array
        message = validate_type({"type": "array"}, "string")
        assert message == 'Expected: an "array" type value\n\nReceived: "string"'


class TestTestOpenAPIObjectErrors:
    def test_missing_response_key_error(self):
        expected_error_message = (
            'The following property is missing in the response data: "one"\n\n'
            "Reference: init.object:key:one\n\n"
            "Hint: Remove the key from your OpenAPI docs, or include it in your API response"
        )
        tester = SchemaTester()
        with pytest.raises(DocumentationError, match=expected_error_message):
            tester.test_openapi_object(
                {"required": ["one"], "properties": {"one": {"type": "int"}}}, {"two": 2}, reference="init"
            )

    def test_missing_schema_key_error(self):
        expected_error_message = (
            'The following property was found in the response, but is missing from the schema definition: "two"\n\n'
            "Reference: init.object:key:two\n\n"
            "Hint: Remove the key from your API response, or include it in your OpenAPI docs"
        )
        tester = SchemaTester()
        with pytest.raises(DocumentationError, match=expected_error_message):
            tester.test_openapi_object(
                {"required": ["one"], "properties": {"one": {"type": "int"}}}, {"one": 1, "two": 2}, reference="init"
            )

    def test_key_in_write_only_properties_error(self):
        expected_error_message = (
            'The following property was found in the response, but is documented as being "writeOnly": "one"\n\n'
            "Reference: init.object:key:one\n\n"
            'Hint: Remove the key from your API response, or remove the "WriteOnly" restriction'
        )
        tester = SchemaTester()
        with pytest.raises(DocumentationError, match=expected_error_message):
            tester.test_openapi_object(
                {"properties": {"one": {"type": "int", "writeOnly": True}}},
                {"one": 1},
                reference="init",
            )


def test_null_error():
    expected_error_message = (
        "Received a null value for a non-nullable schema object\n\n"
        "Reference: init\n\n"
        "Hint: Return a valid type, or document the value as nullable"
    )
    tester = SchemaTester()
    with pytest.raises(DocumentationError, match=expected_error_message):
        tester.test_schema_section({"type": "object"}, None, reference="init")


def test_any_of_error():
    expected_error_message = (
        "Expected data to match one or more of the documented anyOf schema types, but found no matches\n\n"
        "Reference: init.anyOf"
    )
    tester = SchemaTester()
    with pytest.raises(DocumentationError, match=expected_error_message):
        tester.test_schema_section({"anyOf": []}, {}, reference="init")


def test_one_of_error():
    expected_error_message = (
        "Expected data to match one and only one of the oneOf schema types; found 0 matches\n\n" "Reference: init.oneOf"
    )
    tester = SchemaTester()
    with pytest.raises(DocumentationError, match=expected_error_message):
        tester.test_schema_section({"oneOf": []}, {}, reference="init")
