import base64
from typing import Any, Dict, Tuple

import pytest
from faker import Faker

from openapi_tester import SchemaTester
from openapi_tester.constants import (
    OPENAPI_PYTHON_MAPPING,
    VALIDATE_EXCESS_RESPONSE_KEY_ERROR,
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
)
from openapi_tester.exceptions import DocumentationError, OpenAPISchemaError
from openapi_tester.validators import VALIDATOR_MAP
from tests import (
    example_response_types,
    example_schema_array,
    example_schema_integer,
    example_schema_number,
    example_schema_string,
    example_schema_types,
)

tester = SchemaTester()
faker = Faker()

TEST_DATA_MAP: Dict[str, Tuple[Any, Any]] = {
    # by type
    "string": (faker.pystr(), faker.pyint()),
    "file": (faker.pystr(), faker.pyint()),
    "boolean": (faker.pybool(), faker.pystr()),
    "integer": (faker.pyint(), faker.pyfloat()),
    "number": (faker.pyfloat(), faker.pybool()),
    "object": (faker.pydict(), faker.pystr()),
    "array": (faker.pylist(), faker.pystr()),
    # by format
    "byte": (base64.b64encode(faker.pystr().encode("utf-8")).decode("utf-8"), faker.pystr(min_chars=5, max_chars=5)),
    "base64": (base64.b64encode(faker.pystr().encode("utf-8")).decode("utf-8"), faker.pystr(min_chars=5, max_chars=5)),
    "date": (faker.date(), faker.pystr()),
    "date-time": (faker.date_time().isoformat(), faker.pystr()),
    "double": (faker.pyfloat(), faker.pyint()),
    "email": (faker.email(), faker.pystr()),
    "float": (faker.pyfloat(), faker.pyint()),
    "ipv4": (faker.ipv4(), faker.pystr()),
    "ipv6": (faker.ipv6(), faker.pystr()),
    "time": (faker.time(), faker.pystr()),
    "uri": (faker.url(), faker.pystr()),
    "url": (faker.url(), faker.pystr()),
    "uuid": (faker.uuid4(), faker.pystr()),
}


@pytest.mark.parametrize("label", VALIDATOR_MAP.keys())
def test_validator(label: str):
    validator = VALIDATOR_MAP[label]
    good_data, bad_data = TEST_DATA_MAP[label]
    assert validator(good_data) is True
    assert validator(bad_data) is False


def test_type_validation():
    # The examples we've set up should always pass
    for schema, response in zip(example_schema_types, example_response_types):
        tester.test_schema_section(schema, response)

    # An empty array should always pass
    tester.test_schema_section(example_schema_array, [])

    # Schemas with no 'type' property should always pass
    for response in example_response_types:
        tester.test_schema_section({}, response)

    for schema in example_schema_types:
        for response in example_response_types:

            response_python_type = type(response).__name__
            schema_python_type = OPENAPI_PYTHON_MAPPING[schema["type"]]

            if response_python_type in schema_python_type:
                # Skip testing if the types are the same
                # Use `in` because the number type is 'int or float', not just float
                continue

            with pytest.raises(DocumentationError):
                tester.test_schema_section(schema, response)


def test_min_and_max_length_validation():
    # Not adhering to minlength limitations should raise an error
    with pytest.raises(DocumentationError, match=VALIDATE_MIN_LENGTH_ERROR.format(data="a" * 2, min_length=3)):
        tester.test_schema_section(example_schema_string, "a" * 2)

    # Not adhering to maxlength limitations should raise an error
    with pytest.raises(DocumentationError, match=VALIDATE_MAX_LENGTH_ERROR.format(data="a" * 6, max_length=5)):
        tester.test_schema_section(example_schema_string, "a" * 6)


def test_min_and_max_items_validation():
    # Not adhering to minlength limitations should raise an error
    schema = {"type": "array", "items": {"type": "string"}, "minItems": 2}
    with pytest.raises(
        DocumentationError, match=VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=r"\['string'\]", min_length=2)
    ):
        tester.test_schema_section(schema, ["string"])

    # Not adhering to maxlength limitations should raise an error
    schema = {"type": "array", "items": {"type": "string"}, "maxItems": 5}
    with pytest.raises(
        DocumentationError,
        match=VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(
            data=r"\['string', 'string', 'string', 'string', 'string', 'string'\]", max_length=5
        ),
    ):
        tester.test_schema_section(schema, ["string"] * 6)


def test_min_and_max_number_of_properties_validation():
    # Not adhering to minlength limitations should raise an error
    schema = {"type": "object", "properties": {"oneKey": {"type": "string"}}, "minProperties": 2}
    with pytest.raises(DocumentationError, match=VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR[:10]):
        tester.test_schema_section(schema, {"oneKey": "test"})

    # Not adhering to minlength limitations should raise an error
    schema = {
        "type": "object",
        "properties": {"oneKey": {"type": "string"}, "twoKey": {"type": "string"}},
        "maxProperties": 1,
    }
    with pytest.raises(DocumentationError, match=VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR[:10]):
        tester.test_schema_section(schema, {"oneKey": "test", "twoKey": "test"})


def test_additional_properties_allowed():
    schema = {"type": "object", "additionalProperties": True, "properties": {"oneKey": {"type": "string"}}}
    tester.test_schema_section(schema, {"oneKey": "test", "twoKey": "test2"})


def test_additional_properties_specified_as_empty_object_allowed():
    schema = {"type": "object", "additionalProperties": {}, "properties": {"oneKey": {"type": "string"}}}
    tester.test_schema_section(schema, {"oneKey": "test", "twoKey": "test2"})


def test_additional_properties_not_allowed_by_default():
    schema = {"type": "object", "properties": {"oneKey": {"type": "string"}}}
    with pytest.raises(DocumentationError, match=VALIDATE_EXCESS_RESPONSE_KEY_ERROR[:90]):
        tester.test_schema_section(schema, {"oneKey": "test", "twoKey": "test2"})


def test_string_dictionary_specified_as_additional_properties_allowed():
    schema = {"type": "object", "additionalProperties": {"type": "string"}, "properties": {"key_1": {"type": "string"}}}
    tester.test_schema_section(schema, {"key_1": "value_1", "key_2": "value_2", "key_3": "value_3"})


def test_string_dictionary_with_non_string_value_fails_validation():
    schema = {"type": "object", "additionalProperties": {"type": "string"}, "properties": {"key_1": {"type": "string"}}}
    expected_error_message = VALIDATE_TYPE_ERROR.format(article="a", type="string", received=123)
    with pytest.raises(DocumentationError, match=expected_error_message):
        tester.test_schema_section(schema, {"key_1": "value_1", "key_2": 123, "key_3": "value_3"})


def test_object_dictionary_specified_as_additional_properties_allowed():
    schema = {
        "type": "object",
        "properties": {"key_1": {"type": "string"}},
        "additionalProperties": {
            "type": "object",
            "properties": {"key_2": {"type": "string"}, "key_3": {"type": "number"}},
        },
    }
    tester.test_schema_section(
        schema,
        {
            "key_1": "value_1",
            "some_extra_key": {"key_2": "value_2", "key_3": 123},
            "another_extra_key": {"key_2": "value_4", "key_3": 246},
        },
    )


def test_additional_properties_schema_not_validated_in_main_properties():
    schema = {
        "type": "object",
        "properties": {"key_1": {"type": "string"}},
        "additionalProperties": {
            "type": "object",
            "properties": {"key_2": {"type": "string"}, "key_3": {"type": "number"}},
        },
    }
    expected_error_message = VALIDATE_TYPE_ERROR.format(article="an", type="object", received='"value_2"')
    with pytest.raises(DocumentationError, match=expected_error_message):
        tester.test_schema_section(schema, {"key_1": "value_1", "key_2": "value_2", "key_3": 123})


def test_invalid_additional_properties_raises_schema_error():
    schema = {"type": "object", "properties": {"key_1": {"type": "string"}}, "additionalProperties": 123}
    with pytest.raises(OpenAPISchemaError, match="Invalid additionalProperties type"):
        tester.test_schema_section(schema, {"key_1": "value_1", "key_2": "value_2"})


def test_pattern_validation():
    """The a regex pattern can be passed to describe how a string should look"""
    schema = {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$"}

    # Should pass
    tester.test_schema_section(schema, "123-45-6789")

    # Bad pattern should fail
    with pytest.raises(DocumentationError):
        tester.test_schema_section(schema, "test")

    # And if we get compile errors, we need to handle this too
    schema = {"type": "string", "pattern": r"**"}
    with pytest.raises(OpenAPISchemaError):
        tester.test_schema_section(schema, "test")


def test_exclusives_validation():
    """The minimum is included, unless specified"""

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


def test_maximum_and_minimum_validation():
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

    with pytest.raises(DocumentationError):
        tester.test_schema_section({"type": "string", "enum": ["Cat", "Dog"]}, "Turtle")


def test_multiple_of_validation():
    for num, _type in [(5, "integer"), (5, "number")]:
        # Pass
        schema = {"multipleOf": num, "type": _type}
        for integer in [5, 10, 15, 20, 25]:
            tester.test_schema_section(schema, integer)

        # Fail
        with pytest.raises(DocumentationError, match=VALIDATE_MULTIPLE_OF_ERROR.format(data=num + 2, multiple=num)):
            tester.test_schema_section(schema, num + 2)


def test_unique_items_validation():
    schema = {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
    with pytest.raises(DocumentationError):
        tester.test_schema_section(schema, ["identical value", "identical value", "non-identical value"])


def test_date_validation():
    # ISO8601 is valid
    tester.test_schema_section({"type": "string", "format": "date"}, "2040-01-01")

    # This is invalid
    with pytest.raises(DocumentationError):
        tester.test_schema_section({"type": "string", "format": "date"}, "01-31-2019")


def test_datetime_validation():
    # ISO8601 is valid
    tester.test_schema_section({"type": "string", "format": "date-time"}, "2040-01-01 08:00")

    # This is invalid
    with pytest.raises(DocumentationError):
        tester.test_schema_section({"type": "string", "format": "date-time"}, "2040-01-01 0800")


def test_byte_validation():
    tester.test_schema_section({"type": "string", "format": "byte"}, base64.b64encode(b"test123").decode("utf-8"))

    with pytest.raises(DocumentationError):
        tester.test_schema_section({"type": "string", "format": "byte"}, "test123")
