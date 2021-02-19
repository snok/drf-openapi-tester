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
        assert message == "The number of properties in {} is below 2 which is the minimum number of properties required"

    def test_validate_max_properties_error(self):
        message = validate_max_properties({"maxProperties": 1}, {"one": 1, "two": 2})
        assert (
            message == "The number of properties in {'one': 1, 'two': 2} exceeds 1 "
            "which is the maximum number of properties allowed"
        )

    def test_validate_max_items_error(self):
        message = validate_max_items({"maxItems": 1}, [1, 2])
        assert message == "The length of the array [1, 2] exceeds the maximum allowed length of 1"

    def test_validate_min_items_error(self):
        message = validate_min_items({"minItems": 1}, [])
        assert message == "The length of the array [] is below the minimum required length of 1"

    def test_validate_max_length_error(self):
        message = validate_max_length({"maxLength": 1}, "test")
        assert message == 'The length of "test" exceeds the maximum allowed length of 1'

    def test_validate_min_length_error(self):
        message = validate_min_length({"minLength": 5}, "test")
        assert message == 'The length of "test" is below the minimum required length of 5'

    def test_validate_unique_items_error(self):
        message = validate_unique_items({"uniqueItems": True}, [1, 2, 1])
        assert message == "The array [1, 2, 1] must only contain unique items"

    def test_validate_minimum_error(self):
        message = validate_minimum({"minimum": 2}, 0)
        assert message == "The response value 0 is below the minimum required value of 2"

    def test_validate_exclusive_minimum_error(self):
        message = validate_minimum({"minimum": 2, "exclusiveMinimum": True}, 2)
        assert message == "The response value 2 is below the minimum required value of 3"

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
        assert message == 'The string "3" does not validate using the specified pattern: ^[a-z]$'

    # Formatted errors

    def test_validate_enum_error(self):
        message = validate_enum({"enum": ["Cat"]}, "Turtle")
        assert message == 'Expected: a valid enum member, like "Cat"\n\nReceived: "Turtle"'

        message = validate_enum({"enum": ["Cat", "Dog"]}, "Turtle")
        assert message == 'Expected: a valid enum member, like "Cat" or "Dog"\n\nReceived: "Turtle"'

        message = validate_enum({"enum": ["Cat", "Dog", "Hamster", "Parrot"]}, "Turtle")
        assert (
            message == 'Expected: a valid enum member, like "Cat", "Dog", "Hamster", or "Parrot"\n\nReceived: "Turtle"'
        )

    def test_validate_format_error(self):
        # byte
        message = validate_format({"format": "byte"}, "not byte")
        assert message == 'Expected: a "byte" formatted value, like b\'example\'\n\nReceived: "not byte"'

        # base64
        message = validate_format({"format": "base64"}, "not byte")
        assert message == 'Expected: a "base64" formatted value, like b\'ZXhhbXBsZQ==\'\n\nReceived: "not byte"'

        # base64
        message = validate_format({"format": "base64"}, "not base64")
        assert message == 'Expected: a "base64" formatted value, like b\'ZXhhbXBsZQ==\'\n\nReceived: "not base64"'

        # date
        message = validate_format({"format": "date"}, "not date")
        assert message == 'Expected: a "date" formatted value, like "2020-01-22"\n\nReceived: "not date"'

        # date-time
        message = validate_format({"format": "date-time"}, "not date-time")
        assert (
            message == 'Expected: a "date-time" formatted value, like "2020-01-22 08:00"\n\nReceived: "not date-time"'
        )

        # double
        message = validate_format({"format": "double"}, "not double")
        assert message == 'Expected: a "double" formatted value, like 2.22\n\nReceived: "not double"'

        # email
        message = validate_format({"format": "email"}, "not email")
        assert message == 'Expected: an "email" formatted value, like "example@gmail.com"\n\nReceived: "not email"'

        # float
        message = validate_format({"format": "float"}, "not float")
        assert message == 'Expected: a "float" formatted value, like 2.2\n\nReceived: "not float"'

        # ipv4
        message = validate_format({"format": "ipv4"}, "not ipv4")
        assert message == 'Expected: an "ipv4" formatted value, like "192.0.2.235"\n\nReceived: "not ipv4"'

        # ipv6
        message = validate_format({"format": "ipv6"}, "not ipv6")
        assert (
            message
            == 'Expected: an "ipv6" formatted value, like "2001:0db8:85a3:0000:0000:8a2e:0370:7334"\n\nReceived: "not ipv6"'
        )

        # time
        message = validate_format({"format": "time"}, "not time")
        assert message == 'Expected: a "time" formatted value, like "20:00:00"\n\nReceived: "not time"'

        # uri
        message = validate_format({"format": "uri"}, "not uri")
        assert message == 'Expected: a "uri" formatted value, like "https://example.com/"\n\nReceived: "not uri"'

        # url
        message = validate_format({"format": "url"}, "not url")
        assert message == 'Expected: a "url" formatted value, like "https://example.com/"\n\nReceived: "not url"'

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
            'The following property is missing from your response: "one"\n\n'
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
