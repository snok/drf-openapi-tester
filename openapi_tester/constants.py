""" Constants module """
import re

OPENAPI_PYTHON_MAPPING = {
    "boolean": bool.__name__,
    "string": str.__name__,
    "file": str.__name__,
    "array": list.__name__,
    "object": dict.__name__,
    "integer": int.__name__,
    "number": f"{int.__name__} or {float.__name__}",
}

PARAMETER_CAPTURE_REGEX = re.compile(r"({[\w]+})")

# Validation errors
VALIDATE_FORMAT_ERROR = "Mismatched values, expected a value with the format {expected} but received {received}."
VALIDATE_PATTERN_ERROR = "String '{data}' does not validate using the specified pattern: {pattern}"
INVALID_PATTERN_ERROR = "String pattern is not valid regex: {pattern}"
VALIDATE_ENUM_ERROR = "Mismatched values, expected a member of the enum {enum} but received {received}."
VALIDATE_TYPE_ERROR = "Mismatched types, expected {expected} but received {received}."
VALIDATE_MULTIPLE_OF_ERROR = "The response value {data} should be a multiple of {multiple}"
VALIDATE_MINIMUM_ERROR = "The response value {data} exceeds the minimum allowed value of {minimum}"
VALIDATE_MAXIMUM_ERROR = "The response value {data} exceeds the maximum allowed value of {maximum}"
VALIDATE_MIN_LENGTH_ERROR = "The length of {data} exceeds the minimum allowed length of {min_length}"
VALIDATE_MAX_LENGTH_ERROR = "The length of {data} exceeds the maximum allowed length of {max_length}"
VALIDATE_MIN_ARRAY_LENGTH_ERROR = "The length of the array {data} is below the minimum required length of {min_length}"
VALIDATE_MAX_ARRAY_LENGTH_ERROR = "The length of the array {data} exceeds the maximum allowed length of {max_length}"
VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR = (
    "The number of properties in {data} is below the minimum number required, {min_length}"
)
VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR = (
    "The number of properties in {data} exceeds the maximum number allowed, {max_length}"
)
VALIDATE_UNIQUE_ITEMS_ERROR = "The schema specifies that the array must have unique items, but items are not unique."

VALIDATE_RESPONSE_TYPE_ERROR = "Expected response to be an instance of DRF Response"

NONE_ERROR = "Mismatched content. Expected {expected} but received NoneType"
MISSING_RESPONSE_KEY_ERROR = "The following property is missing from the tested data: {missing_key}."
MISSING_PROPERTY_KEY_ERROR = (
    "The following key was found in your required properties, but is missing from properties: {missing_key}"
)
EXCESS_RESPONSE_KEY_ERROR = (
    "The following property was found in the response, but is missing from the schema definition: {excess_key}."
)
UNDOCUMENTED_SCHEMA_SECTION_ERROR = "Error: Unsuccessfully tried to index the OpenAPI schema by `{key}`. {error_addon}"
ONE_OF_ERROR = "Expected data to match one and only one of the oneOf schema types; found {matches} matches."
ANY_OF_ERROR = "Expected data to match one or more of the documented anyOf schema types, but found no matches."
INIT_ERROR = "Unable to configure loader."
