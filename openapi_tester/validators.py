""" OpenAPI schema validators """
import re
from typing import TYPE_CHECKING, Optional

from django.utils.dateparse import parse_date, parse_datetime

from openapi_tester import DocumentationError
from openapi_tester.constants import (
    INVALID_PATTERN_ERROR,
    OPENAPI_FORMAT_EXAMPLES,
    OPENAPI_PYTHON_MAPPING,
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
    VALIDATE_PATTERN_ERROR,
    VALIDATE_TYPE_ERROR,
    VALIDATE_UNIQUE_ITEMS_ERROR,
)
from openapi_tester.utils import get_schema_type

if TYPE_CHECKING:
    from openapi_tester.schema_tester import Instance


def validate_enum(instance: "Instance") -> None:
    enum = instance.schema_section.get("enum")
    if enum and instance.data not in enum:
        raise DocumentationError(message=VALIDATE_ENUM_ERROR, example=enum, instance=instance)


def validate_pattern(instance: "Instance") -> None:
    pattern = instance.schema_section.get("pattern")
    if pattern:
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise DocumentationError(INVALID_PATTERN_ERROR.format(pattern=pattern)) from e
        if not compiled_pattern.match(instance.data):
            raise DocumentationError(
                message=VALIDATE_PATTERN_ERROR.format(data=instance.data, pattern=pattern),
                example=pattern,
                instance=instance,
            )


def validate_format(instance: "Instance") -> None:
    schema_format = instance.schema_section.get("format")
    if schema_format:
        valid = True
        if schema_format in ["double", "float"]:
            valid = isinstance(instance.data, float)
        elif schema_format == "byte":
            valid = isinstance(instance.data, bytes)
        elif schema_format in ["date", "date-time"]:
            parser = parse_date if schema_format == "date" else parse_datetime
            valid = parser(instance.data) is not None
        if not valid:
            raise DocumentationError(
                message=VALIDATE_FORMAT_ERROR.format(format=schema_format),
                example=OPENAPI_FORMAT_EXAMPLES[schema_format],
                instance=instance,
            )


def validate_openapi_type(instance: "Instance") -> None:
    schema_type = get_schema_type(instance.schema_section)
    if schema_type:
        valid = True
        if schema_type in ["file", "string"]:
            valid = isinstance(instance.data, (str, bytes))
        elif schema_type == "boolean":
            valid = isinstance(instance.data, bool)
        elif schema_type == "integer":
            valid = isinstance(instance.data, int) and not isinstance(instance.data, bool)
        elif schema_type == "number":
            valid = isinstance(instance.data, (int, float)) and not isinstance(instance.data, bool)
        elif schema_type == "object":
            valid = isinstance(instance.data, dict)
        elif schema_type == "array":
            valid = isinstance(instance.data, list)
        if not valid:
            raise DocumentationError(
                message=VALIDATE_TYPE_ERROR.format(type=OPENAPI_PYTHON_MAPPING[instance.schema_type]), instance=instance
            )


def validate_multiple_of(instance: "Instance") -> None:
    multiple_of = instance.schema_section.get("multipleOf")
    if multiple_of and instance.data % multiple_of != 0:
        error = VALIDATE_MULTIPLE_OF_ERROR.format(data=instance.data, multiple=multiple_of)
        raise DocumentationError(message=error)


def validate_min_and_max(instance: "Instance") -> None:
    minimum = instance.schema_section.get("minimum")
    maximum = instance.schema_section.get("maximum")
    exclusive_minimum = instance.schema_section.get("exclusiveMinimum")
    exclusive_maximum = instance.schema_section.get("exclusiveMaximum")
    error = ""
    if minimum and exclusive_minimum and instance.data <= minimum:
        error = VALIDATE_MINIMUM_ERROR.format(data=instance.data, minimum=minimum + 1)
    if minimum and not exclusive_minimum and instance.data < minimum:
        error = VALIDATE_MINIMUM_ERROR.format(data=instance.data, minimum=minimum)
    if maximum and exclusive_maximum and instance.data >= maximum:
        error = VALIDATE_MAXIMUM_ERROR.format(data=instance.data, maximum=maximum - 1)
    if maximum and not exclusive_maximum and instance.data > maximum:
        error = VALIDATE_MAXIMUM_ERROR.format(data=instance.data, maximum=maximum)
    if error:
        raise DocumentationError(message=error)


def validate_unique_items(instance: "Instance") -> None:
    unique_items = instance.schema_section.get("uniqueItems")
    if unique_items and len(set(instance.data)) != len(instance.data):
        raise DocumentationError(
            message=VALIDATE_UNIQUE_ITEMS_ERROR,
        )
    # TODO: handle deep dictionary comparison - for lists of dicts


def validate_length(instance: "Instance") -> None:
    min_length: Optional[int] = instance.schema_section.get("minLength")
    max_length: Optional[int] = instance.schema_section.get("maxLength")
    error = ""
    if min_length and len(instance.data) < min_length:
        error = VALIDATE_MIN_LENGTH_ERROR.format(data=instance.data, min_length=min_length)
    if max_length and len(instance.data) > max_length:
        error = VALIDATE_MAX_LENGTH_ERROR.format(data=instance.data, max_length=max_length)
    if error:
        raise DocumentationError(message=error)


def validate_array_length(instance: "Instance") -> None:
    min_length: Optional[int] = instance.schema_section.get("minItems")
    max_length: Optional[int] = instance.schema_section.get("maxItems")
    error = ""
    if min_length and len(instance.data) < min_length:
        error = VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=instance.data, min_length=min_length)
    if max_length and len(instance.data) > max_length:
        error = VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(data=instance.data, max_length=max_length)
    if error:
        raise DocumentationError(message=error)


def validate_number_of_properties(instance: "Instance") -> None:
    min_properties: Optional[int] = instance.schema_section.get("minProperties")
    max_properties: Optional[int] = instance.schema_section.get("maxProperties")
    error = ""
    if min_properties and len(instance.data) < min_properties:
        error = VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=instance.data, min_length=min_properties)
    if max_properties and len(instance.data) > max_properties:
        error = VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=instance.data, max_length=max_properties)
    if error:
        raise DocumentationError(message=error)


default_validators = [
    validate_enum,
    validate_openapi_type,
    validate_format,
    validate_pattern,
    validate_multiple_of,
    validate_min_and_max,
    validate_length,
    validate_unique_items,
    validate_array_length,
    validate_number_of_properties,
]
