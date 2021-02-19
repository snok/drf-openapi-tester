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
VALIDATE_FORMAT_ERROR = 'Expected: {article} "{format}" formatted value, like {example}\n\nReceived: {received}'
VALIDATE_PATTERN_ERROR = 'The string "{data}" does not validate using the specified pattern: {pattern}'
INVALID_PATTERN_ERROR = "String pattern is not valid regex: {pattern}"
VALIDATE_ENUM_ERROR = "Expected: {expected}\n\nReceived: {received}"
VALIDATE_TYPE_ERROR = 'Expected: {article} "{type}" type value\n\nReceived: {received}'
VALIDATE_MULTIPLE_OF_ERROR = "The response value {data} should be a multiple of {multiple}"
VALIDATE_MINIMUM_ERROR = "The response value {data} is below the minimum required value of {minimum}"
VALIDATE_MAXIMUM_ERROR = "The response value {data} exceeds the maximum allowed value of {maximum}"
VALIDATE_MIN_LENGTH_ERROR = 'The length of "{data}" is below the minimum required length of {min_length}'
VALIDATE_MAX_LENGTH_ERROR = 'The length of "{data}" exceeds the maximum allowed length of {max_length}'
VALIDATE_MIN_ARRAY_LENGTH_ERROR = "The length of the array {data} is below the minimum required length of {min_length}"
VALIDATE_MAX_ARRAY_LENGTH_ERROR = "The length of the array {data} exceeds the maximum allowed length of {max_length}"
VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR = (
    "The number of properties in {data} is below {min_length} which is the minimum number of properties required"
)
VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR = (
    "The number of properties in {data} exceeds {max_length} which is the maximum number of properties allowed"
)
VALIDATE_UNIQUE_ITEMS_ERROR = "The array {data} must only contain unique items"
VALIDATE_NONE_ERROR = "Mismatched content. Expected {expected} but received NoneType"
VALIDATE_MISSING_RESPONSE_KEY_ERROR = "The following property is missing from the tested data: {missing_key}."
VALIDATE_MISSING_PROPERTY_KEY_ERROR = (
    "The following key was found in your required properties, but is missing from properties: {missing_key}"
)
VALIDATE_EXCESS_RESPONSE_KEY_ERROR = (
    "The following property was found in the response, but is missing from the schema definition: {excess_key}."
)
VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR = (
    "The following property was found in the response, but is documented as being `WriteOnly`: {write_only_key}."
)
VALIDATE_ONE_OF_ERROR = "Expected data to match one and only one of the oneOf schema types; found {matches} matches."
VALIDATE_ANY_OF_ERROR = "Expected data to match one or more of the documented anyOf schema types, but found no matches."
UNDOCUMENTED_SCHEMA_SECTION_ERROR = "Error: Unsuccessfully tried to index the OpenAPI schema by `{key}`. {error_addon}"
INIT_ERROR = "Unable to configure loader."
