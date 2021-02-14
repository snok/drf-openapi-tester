import pytest

from openapi_tester import OPENAPI_PYTHON_MAPPING, DocumentationError, OpenAPISchemaError, SchemaTester
from openapi_tester.constants import (
    EXCESS_RESPONSE_KEY_ERROR,
    MISSING_RESPONSE_KEY_ERROR,
    NONE_ERROR,
    ONE_OF_ERROR,
    VALIDATE_ENUM_ERROR,
    VALIDATE_FORMAT_ERROR,
    VALIDATE_MAX_ARRAY_LENGTH_ERROR,
    VALIDATE_MAX_LENGTH_ERROR,
    VALIDATE_MAXIMUM_ERROR,
    VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR,
    VALIDATE_MIN_ARRAY_LENGTH_ERROR,
    VALIDATE_MIN_LENGTH_ERROR,
    VALIDATE_MINIMUM_ERROR,
    VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR,
    VALIDATE_MULTIPLE_OF_ERROR,
    VALIDATE_TYPE_ERROR,
    VALIDATE_UNIQUE_ITEMS_ERROR,
)

tester = SchemaTester()

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

docs_any_of_example = {
    "type": "object",
    "anyOf": [
        {
            "required": ["age"],
            "properties": {
                "age": {"type": "integer"},
                "nickname": {"type": "string"},
            },
        },
        {
            "required": ["pet_type"],
            "properties": {
                "pet_type": {"type": "string", "enum": ["Cat", "Dog"]},
                "hunts": {"type": "boolean"},
            },
        },
    ],
}


def test_successful_type_validation():
    # The examples we've set up should always pass
    for schema, response in zip(example_schema_types, example_response_types):
        tester.test_schema_section(schema, response)

    # An empty array should always pass
    tester.test_schema_section(example_schema_array, [])

    # Schemas with no 'type' property should always pass
    for response in example_response_types:
        tester.test_schema_section({}, response)


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


def test_unsuccessful_type_validation():
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


def test_min_and_max_length():
    # Not adhering to minlength limitations should raise an error
    with pytest.raises(DocumentationError, match=VALIDATE_MIN_LENGTH_ERROR.format(data="a" * 2, min_length=3)):
        tester.test_schema_section(example_schema_string, "a" * 2)

    # Not adhering to maxlength limitations should raise an error
    with pytest.raises(DocumentationError, match=VALIDATE_MAX_LENGTH_ERROR.format(data="a" * 6, max_length=5)):
        tester.test_schema_section(example_schema_string, "a" * 6)


def test_min_and_max_items():
    # Not adhering to minlength limitations should raise an error
    with pytest.raises(
        DocumentationError, match=VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=r"\['string'\]", min_length=2)
    ):
        schema = {"type": "array", "items": {"type": "string"}, "minItems": 2}
        tester.test_schema_section(schema, ["string"])

    # Not adhering to maxlength limitations should raise an error
    with pytest.raises(
        DocumentationError,
        match=VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(
            data=r"\['string', 'string', 'string', 'string', 'string', 'string'\]", max_length=5
        ),
    ):
        schema = {"type": "array", "items": {"type": "string"}, "maxItems": 5}
        tester.test_schema_section(schema, ["string"] * 6)


def test_min_and_max_number_of_properties():
    # Not adhering to minlength limitations should raise an error
    with pytest.raises(DocumentationError, match=VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR[:10]):
        schema = {"type": "object", "properties": {"oneKey": {"type": "string"}}, "minProperties": 2}
        tester.test_schema_section(schema, {"oneKey": "test"})

    # Not adhering to minlength limitations should raise an error
    with pytest.raises(DocumentationError, match=VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR[:10]):
        schema = {
            "type": "object",
            "properties": {"oneKey": {"type": "string"}, "twoKey": {"type": "string"}},
            "maxProperties": 1,
        }
        tester.test_schema_section(schema, {"oneKey": "test", "twoKey": "test"})


def test_pattern():
    """ The a regex pattern can be passed to describe how a string should look """
    schema = {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$"}

    # Should pass
    tester.test_schema_section(schema, "123-45-6789")

    # Bad pattern should fail
    with pytest.raises(DocumentationError, match="String 'test' does not validate using the specified pattern"):
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


def test_maximum_and_minimum():
    # Not adhering to maximum limitations should raise an error
    for num, schema in [(6, example_schema_integer), (6.12, example_schema_number)]:
        with pytest.raises(DocumentationError, match=VALIDATE_MAXIMUM_ERROR.format(data=num, maximum=5)):
            tester.test_schema_section(schema, num)

    # Not adhering to minimum limitations should raise an error
    for num, schema in [(2, example_schema_integer), (2.22, example_schema_number)]:
        with pytest.raises(DocumentationError, match=VALIDATE_MINIMUM_ERROR.format(data=num, minimum=3)):
            tester.test_schema_section(schema, num)


def test_enum_validation():
    tester.test_schema_section({"type": "string", "enum": ["Cat", "Dog"]}, "Cat")
    tester.test_schema_section({"type": "string", "enum": ["Cat", "Dog"]}, "Dog")

    with pytest.raises(
        DocumentationError, match=VALIDATE_ENUM_ERROR.format(enum=r"\['Cat', 'Dog'\]", received="Turtle")
    ):
        tester.test_schema_section({"type": "string", "enum": ["Cat", "Dog"]}, "Turtle")


def test_multiple_of():
    for num, _type in [(5, "integer"), (5, "number")]:
        # Pass
        schema = {"multipleOf": num, "type": _type}
        for integer in [5, 10, 15, 20, 25]:
            tester.test_schema_section(schema, integer)

        # Fail
        with pytest.raises(DocumentationError, match=VALIDATE_MULTIPLE_OF_ERROR.format(data=num + 2, multiple=num)):
            tester.test_schema_section(schema, num + 2)


def test_unique_items_validator():
    with pytest.raises(DocumentationError, match=VALIDATE_UNIQUE_ITEMS_ERROR):
        schema = {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
        tester.test_schema_section(schema, ["identical value", "identical value", "non-identical value"])


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


def test_response_is_missing_keys():
    with pytest.raises(DocumentationError, match=MISSING_RESPONSE_KEY_ERROR.format(missing_key="value")):
        # If a required key is missing, we should raise an error
        required_key = {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]}
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


def test_any_of_handling():
    """
    This test makes sure our anyOf implementation works as described in the official example docs:
    https://swagger.io/docs/specification/data-models/oneof-anyof-allof-not/#anyof
    """
    tester.test_schema_section(docs_any_of_example, {"age": 50})
    tester.test_schema_section(docs_any_of_example, {"pet_type": "Cat", "hunts": True})
    tester.test_schema_section(docs_any_of_example, {"nickname": "Fido", "pet_type": "Dog", "age": 44})

    with pytest.raises(DocumentationError):
        tester.test_schema_section(docs_any_of_example, {"nickname": "Mr. Paws", "hunts": False})


def test_one_of():
    all_types = [
        {"type": "string"},
        {"type": "number"},
        {"type": "integer"},
        {"type": "boolean"},
        {"type": "array", "items": {}},
        {"type": "object"},
    ]

    # Make sure integers are validated correctly
    non_int_types = all_types[:1] + all_types[3:]
    int_types = all_types[1:3]
    int_value = 1
    for type in non_int_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, int_value)
    for type in int_types:
        tester.test_schema_section({"oneOf": [type]}, int_value)

    # Make sure strings are validated correctly
    non_string_types = all_types[1:]
    string_types = all_types[:1]
    string_value = "test"
    for type in non_string_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, string_value)
    for type in string_types:
        tester.test_schema_section({"oneOf": [type]}, string_value)

    # Make sure booleans are validated correctly
    non_boolean_types = all_types[:3] + all_types[4:]
    boolean_types = [all_types[3]]
    boolean_value = False
    for type in non_boolean_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, boolean_value)
    for type in boolean_types:
        tester.test_schema_section({"oneOf": [type]}, boolean_value)

    # Make sure arrays are validated correctly
    non_array_types = all_types[:4] + all_types[5:]
    array_types = [all_types[4]]
    array_value = []
    for type in non_array_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, array_value)
    for type in array_types:
        tester.test_schema_section({"oneOf": [type]}, array_value)

    # Make sure arrays are validated correctly
    non_object_types = all_types[:5]
    object_types = [all_types[5]]
    object_value = {}
    for type in non_object_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, object_value)
    for type in object_types:
        tester.test_schema_section({"oneOf": [type]}, object_value)

    # Make sure we raise the appropriate error when we find several matches
    with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=2)):
        tester.test_schema_section(
            {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "array", "items": {}},
                    {"type": "object"},
                ]
            },
            1,
        )

    # Make sure we raise the appropriate error when we find no matches
    with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
        tester.test_schema_section(
            {
                "oneOf": [
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "array", "items": {}},
                    {"type": "object"},
                ]
            },
            "test",
        )
