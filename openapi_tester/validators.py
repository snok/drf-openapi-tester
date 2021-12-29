""" Schema Validators """
from __future__ import annotations

import base64
import re
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator, validate_ipv4_address, validate_ipv6_address
from django.utils.dateparse import parse_date, parse_datetime, parse_time

from openapi_tester.constants import (
    INVALID_PATTERN_ERROR,
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
from openapi_tester.exceptions import OpenAPISchemaError

if TYPE_CHECKING:
    from typing import Any, Callable


def create_validator(validation_fn: Callable, wrap_as_validator: bool = False) -> Callable[[Any], bool]:
    def wrapped(value: Any) -> bool:
        try:
            return bool(validation_fn(value)) or not wrap_as_validator
        except (ValueError, ValidationError):
            return False

    return wrapped


number_format_validator = create_validator(
    lambda x: isinstance(x, float) if x != 0 else isinstance(x, (int, float)), True
)

base64_format_validator = create_validator(lambda x: base64.b64encode(base64.b64decode(x, validate=True)) == x)

VALIDATOR_MAP: dict[str, Callable] = {
    # by type
    "string": create_validator(lambda x: isinstance(x, str), True),
    "file": create_validator(lambda x: isinstance(x, str), True),
    "boolean": create_validator(lambda x: isinstance(x, bool), True),
    "integer": create_validator(lambda x: isinstance(x, int) and not isinstance(x, bool), True),
    "number": create_validator(lambda x: isinstance(x, (float, int)) and not isinstance(x, bool), True),
    "object": create_validator(lambda x: isinstance(x, dict), True),
    "array": create_validator(lambda x: isinstance(x, list), True),
    # by format
    "byte": base64_format_validator,
    "base64": base64_format_validator,
    "date": create_validator(parse_date, True),
    "date-time": create_validator(parse_datetime, True),
    "double": number_format_validator,
    "email": create_validator(EmailValidator()),
    "float": number_format_validator,
    "ipv4": create_validator(validate_ipv4_address),
    "ipv6": create_validator(validate_ipv6_address),
    "time": create_validator(parse_time, True),
    "uri": create_validator(URLValidator()),
    "url": create_validator(URLValidator()),
    "uuid": create_validator(UUID),
}


def validate_type(schema_section: dict[str, Any], data: Any) -> str | None:
    schema_type: str = schema_section.get("type", "object")
    if not VALIDATOR_MAP[schema_type](data):
        an_articles = ["integer", "object", "array"]
        return VALIDATE_TYPE_ERROR.format(
            article="a" if schema_type not in an_articles else "an",
            type=schema_type,
            received=f'"{data}"' if isinstance(data, str) else data,
        )
    return None


def validate_format(schema_section: dict[str, Any], data: Any) -> str | None:
    schema_format: str = schema_section.get("format", "")
    if schema_format in VALIDATOR_MAP and not VALIDATOR_MAP[schema_format](data):
        return VALIDATE_FORMAT_ERROR.format(
            article="an" if format in ["ipv4", "ipv6", "email"] else "a",
            format=schema_format,
            received=f'"{data}"',
        )
    return None


def validate_enum(schema_section: dict[str, Any], data: Any) -> str | None:
    enum = schema_section.get("enum")
    if enum and data not in enum:
        return VALIDATE_ENUM_ERROR.format(enum=schema_section["enum"], received=f'"{data}"')
    return None


def validate_pattern(schema_section: dict[str, Any], data: str) -> str | None:
    pattern = schema_section.get("pattern")
    if not pattern:
        return None
    try:
        compiled_pattern = re.compile(pattern)
    except re.error as e:
        raise OpenAPISchemaError(INVALID_PATTERN_ERROR.format(pattern=pattern)) from e
    if not compiled_pattern.match(str(data)):
        return VALIDATE_PATTERN_ERROR.format(data=data, pattern=pattern)
    return None


def validate_multiple_of(schema_section: dict[str, Any], data: int | float) -> str | None:
    multiple = schema_section.get("multipleOf")
    if multiple and data % multiple != 0:
        return VALIDATE_MULTIPLE_OF_ERROR.format(data=data, multiple=multiple)
    return None


def validate_maximum(schema_section: dict[str, Any], data: int | float) -> str | None:
    maximum = schema_section.get("maximum")
    exclusive_maximum = schema_section.get("exclusiveMaximum")
    if maximum and exclusive_maximum and data >= maximum:
        return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum - 1)
    if maximum and not exclusive_maximum and data > maximum:
        return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum)
    return None


def validate_minimum(schema_section: dict[str, Any], data: int | float) -> str | None:
    minimum = schema_section.get("minimum")
    exclusive_minimum = schema_section.get("exclusiveMinimum")
    if minimum and exclusive_minimum and data <= minimum:
        return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum + 1)
    if minimum and not exclusive_minimum and data < minimum:
        return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum)
    return None


def validate_unique_items(schema_section: dict[str, Any], data: list[Any]) -> str | None:
    unique_items = schema_section.get("uniqueItems")
    if unique_items and len(set(data)) != len(data):
        return VALIDATE_UNIQUE_ITEMS_ERROR.format(data=data)
    # TODO: handle deep dictionary comparison - for lists of dicts
    return None


def validate_min_length(schema_section: dict[str, Any], data: str) -> str | None:
    min_length: int | None = schema_section.get("minLength")
    if min_length and len(data) < min_length:
        return VALIDATE_MIN_LENGTH_ERROR.format(data=data, min_length=min_length)
    return None


def validate_max_length(schema_section: dict[str, Any], data: str) -> str | None:
    max_length: int | None = schema_section.get("maxLength")
    if max_length and len(data) > max_length:
        return VALIDATE_MAX_LENGTH_ERROR.format(data=data, max_length=max_length)
    return None


def validate_min_items(schema_section: dict[str, Any], data: list) -> str | None:
    min_length: int | None = schema_section.get("minItems")
    if min_length and len(data) < min_length:
        return VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=data, min_length=min_length)
    return None


def validate_max_items(schema_section: dict[str, Any], data: list) -> str | None:
    max_length: int | None = schema_section.get("maxItems")
    if max_length and len(data) > max_length:
        return VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(data=data, max_length=max_length)
    return None


def validate_min_properties(schema_section: dict[str, Any], data: dict) -> str | None:
    min_properties: int | None = schema_section.get("minProperties")
    if min_properties and len(data.keys()) < int(min_properties):
        return VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=data, min_length=min_properties)
    return None


def validate_max_properties(schema_section: dict[str, Any], data: dict) -> str | None:
    max_properties: int | None = schema_section.get("maxProperties")
    if max_properties and len(data.keys()) > int(max_properties):
        return VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=data, max_length=max_properties)
    return None
