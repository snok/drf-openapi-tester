""" Constants module """
OPENAPI_PYTHON_MAPPING = {
    "boolean": bool.__name__,
    "string": str.__name__,
    "file": str.__name__,
    "array": list.__name__,
    "object": dict.__name__,
    "integer": int.__name__,
    "number": f"{int.__name__} or {float.__name__}",
}

# Validation errors
VALIDATE_FORMAT_ERROR = 'Expected: {article} "{format}" formatted value\n\nReceived: {received}'
VALIDATE_PATTERN_ERROR = 'The string "{data}" does not match the specified pattern: {pattern}'
INVALID_PATTERN_ERROR = "String pattern is not valid regex: {pattern}"
VALIDATE_ENUM_ERROR = "Expected: a member of the enum {enum}\n\nReceived: {received}"
VALIDATE_TYPE_ERROR = 'Expected: {article} "{type}" type value\n\nReceived: {received}'
VALIDATE_MULTIPLE_OF_ERROR = "The value {data} should be a multiple of {multiple}"
VALIDATE_MINIMUM_ERROR = "The value {data} is lower than the specified minimum of {minimum}"
VALIDATE_MAXIMUM_ERROR = "The value {data} exceeds the maximum allowed value of {maximum}"
VALIDATE_MIN_LENGTH_ERROR = 'The length of "{data}" is shorter than the specified minimum length of {min_length}'
VALIDATE_MAX_LENGTH_ERROR = 'The length of "{data}" exceeds the specified maximum length of {max_length}'
VALIDATE_MIN_ARRAY_LENGTH_ERROR = (
    "The length of the array {data} is shorter than the specified minimum length of {min_length}"
)
VALIDATE_MAX_ARRAY_LENGTH_ERROR = "The length of the array {data} exceeds the specified maximum length of {max_length}"
VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR = (
    "The number of properties in {data} is fewer than the specified minimum number of properties of {min_length}"
)
VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR = (
    "The number of properties in {data} exceeds the specified maximum number of properties of {max_length}"
)
VALIDATE_UNIQUE_ITEMS_ERROR = "The array {data} must contain unique items only"
VALIDATE_NONE_ERROR = "Received a null value for a non-nullable schema object"
VALIDATE_MISSING_KEY_ERROR = 'The following property is missing in the {http_message} data: "{missing_key}"'
VALIDATE_EXCESS_KEY_ERROR = (
    'The following property was found in the {http_message}, but is missing from the schema definition: "{excess_key}"'
)
VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR = (
    'The following property was found in the response, but is documented as being "writeOnly": "{write_only_key}"'
)
VALIDATE_ONE_OF_ERROR = "Expected data to match one and only one of the oneOf schema types; found {matches} matches"
VALIDATE_ANY_OF_ERROR = "Expected data to match one or more of the documented anyOf schema types, but found no matches"
UNDOCUMENTED_SCHEMA_SECTION_ERROR = "Error: Unsuccessfully tried to index the OpenAPI schema by `{key}`. {error_addon}"
INIT_ERROR = "Unable to configure loader"
