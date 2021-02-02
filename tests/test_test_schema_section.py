import pytest

from openapi_tester import DocumentationError, OpenAPISchemaError, SchemaTester
from openapi_tester.constants import (
    EXCESS_RESPONSE_KEY_ERROR,
    MISSING_RESPONSE_KEY_ERROR,
    NONE_ERROR,
    OPENAPI_PYTHON_MAPPING,
    VALIDATE_FORMAT_ERROR,
    VALIDATE_MAX_LENGTH_ERROR,
    VALIDATE_MAXIMUM_ERROR,
    VALIDATE_MIN_LENGTH_ERROR,
    VALIDATE_MINIMUM_ERROR,
    VALIDATE_MULTIPLE_OF_ERROR,
    VALIDATE_TYPE_ERROR,
)

example_schema_array = {"type": "array", "items": {"type": "string"}}
example_array = ["string"]
example_schema_integer = {"type": "integer", "minimum": 3, "maximum": 5}
example_integer = 3
example_schema_number = {"type": "number", "minimum": 3, "maximum": 5}
example_number = 3.2
example_schema_object = {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]}
example_object = {"value": 1}
example_schema_string = {"type": "string", "minLength": 3, "maxLength": 5}
example_string = "str"

example_response_types = [example_array, example_integer, example_number, example_object, example_string]
example_schema_types = [
    example_schema_array,
    example_schema_integer,
    example_schema_number,
    example_schema_object,
    example_schema_string,
]

tester = SchemaTester()


def test_nothing_wrong():
    """ This should always pass """
    for schema, response in zip(example_schema_types, example_response_types):
        tester.test_schema_section(schema, response)


def test_empty_list():
    """ An empty array should always pass """
    tester.test_schema_section(example_schema_array, [])


def test_nullable():
    for schema in example_schema_types:
        # A null value should always raise an error
        with pytest.raises(
            DocumentationError, match=NONE_ERROR.format(expected=OPENAPI_PYTHON_MAPPING[schema["type"]])
        ):
            tester.test_schema_section(schema, None)

        # Unless the schema specifies it should be nullable

        # OpenAPI 3+
        schema["nullable"] = True
        tester.test_schema_section(schema, None)

        # Swagger 2.0
        del schema["nullable"]
        schema["x-nullable"] = True
        tester.test_schema_section(schema, None)


def test_wrong_type():
    """ Type mismatches should raise errors """
    for schema in example_schema_types:
        for response in example_response_types:

            response_python_type = type(response).__name__
            schema_python_type = OPENAPI_PYTHON_MAPPING[schema["type"]]

            if response_python_type in schema_python_type:
                # Skip testing if the types are the same
                # Use `in` because the number type is 'int or float', not just float
                continue

            with pytest.raises(
                DocumentationError,
                match=VALIDATE_TYPE_ERROR.format(expected=schema_python_type, received=response_python_type),
            ):
                tester.test_schema_section(schema, response)


def test_min_length_violated():
    """ Not adhering to minlength limitations should raise an error """
    with pytest.raises(DocumentationError, match=VALIDATE_MIN_LENGTH_ERROR.format(data="a" * 2, min_length=3)):
        tester.test_schema_section(example_schema_string, "a" * 2)


def test_max_length_violated():
    """ Not adhering to maxlength limitations should raise an error """
    with pytest.raises(DocumentationError, match=VALIDATE_MAX_LENGTH_ERROR.format(data="a" * 6, max_length=5)):
        tester.test_schema_section(example_schema_string, "a" * 6)


def test_date_format():
    # ISO8601 is valid
    tester.test_schema_section({"type": "string", "format": "date"}, "2040-01-01")

    # This is invalid
    with pytest.raises(DocumentationError, match=VALIDATE_FORMAT_ERROR.format(expected="date", received="01-31-2019")):
        tester.test_schema_section({"type": "string", "format": "date"}, "01-31-2019")


def test_datetime():
    # ISO8601 is valid
    tester.test_schema_section({"type": "string", "format": "date-time"}, "2040-01-01 08:00")

    # This is invalid
    with pytest.raises(
        DocumentationError, match=VALIDATE_FORMAT_ERROR.format(expected="date-time", received="2040-01-01 0800")
    ):
        tester.test_schema_section({"type": "string", "format": "date-time"}, "2040-01-01 0800")


def test_byte():
    tester.test_schema_section({"type": "string", "format": "byte"}, b"test")

    with pytest.raises(DocumentationError, match=VALIDATE_FORMAT_ERROR.format(expected="byte", received="test")):
        tester.test_schema_section({"type": "string", "format": "byte"}, "test")


def test_pattern():
    """ The a regex pattern can be passed to describe how a string should look """
    schema = {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$"}

    # Should pass
    tester.test_schema_section(schema, "123-45-6789")

    # Bad pattern should fail
    with pytest.raises(DocumentationError, match="Error: String 'test' does not validate using the specified pattern:"):
        tester.test_schema_section(schema, "test")

    # And if we get compile errors, we need to handle this too
    schema = {"type": "string", "pattern": r"**"}
    with pytest.raises(OpenAPISchemaError):
        tester.test_schema_section(schema, "test")


def test_exclusives():
    """ The minimum is included, unless specified """

    # Pass when set to minimum
    schema = {"type": "integer", "minimum": 3, "exclusiveMinimum": False, "maximum": 5}
    tester.test_schema_section(schema, 3)

    # Fail when we exclude the minimum
    schema["exclusiveMinimum"] = True
    with pytest.raises(DocumentationError, match=VALIDATE_MINIMUM_ERROR.format(data=3, minimum=4)):
        tester.test_schema_section(schema, 3)

    # Fail when we exclude the maximum
    schema["exclusiveMaximum"] = True
    with pytest.raises(DocumentationError, match=VALIDATE_MAXIMUM_ERROR.format(data=5, maximum=4)):
        tester.test_schema_section(schema, 5)

    # Pass when we include the maximum
    schema["exclusiveMaximum"] = False
    tester.test_schema_section(schema, 5)


def test_maximum_violated():
    """ Not adhering to maximum limitations should raise an error """
    for num, schema in [(6, example_schema_integer), (6.12, example_schema_number)]:
        with pytest.raises(DocumentationError, match=VALIDATE_MAXIMUM_ERROR.format(data=num, maximum=5)):
            tester.test_schema_section(schema, num)


def test_minimum_violated():
    """ Not adhering to minimum limitations should raise an error """
    for num, schema in [(2, example_schema_integer), (2.22, example_schema_number)]:
        with pytest.raises(DocumentationError, match=VALIDATE_MINIMUM_ERROR.format(data=num, minimum=3)):
            tester.test_schema_section(schema, num)


def test_multiple_of():
    for num, _type in [(5, "integer"), (5, "number")]:
        # Pass
        schema = {"multipleOf": num, "type": _type}
        for integer in [5, 10, 15, 20, 25]:
            tester.test_schema_section(schema, integer)

        # Fail
        with pytest.raises(DocumentationError, match=VALIDATE_MULTIPLE_OF_ERROR.format(data=num + 2, multiple=num)):
            tester.test_schema_section(schema, num + 2)


def test_response_is_missing_keys():
    # If a required key is missing, we should raise an error
    required_key = {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]}
    with pytest.raises(DocumentationError, match=MISSING_RESPONSE_KEY_ERROR.format(missing_key="value")):
        tester.test_schema_section(required_key, {})

    # If not required, it should pass
    optional_key = {"type": "object", "properties": {"value": {"type": "integer"}}}
    tester.test_schema_section(optional_key, {})


def test_schema_object_is_missing_keys():
    """ Excess keys in a response should raise an error """
    with pytest.raises(
        DocumentationError,
        match=EXCESS_RESPONSE_KEY_ERROR.format(excess_key="value"),
    ):
        schema = {"type": "object", "properties": {}}
        tester.test_schema_section(schema, example_object)
