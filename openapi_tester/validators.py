""" Schema Validators """
import base64
import re
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator, validate_ipv4_address, validate_ipv6_address
from django.utils.dateparse import parse_date, parse_datetime, parse_time

from openapi_tester import OpenAPISchemaError
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


def create_validator(validation_fn: Callable, wrap_as_validator: bool = False) -> Callable:
    def wrapped(value: Any):
        try:
            return bool(validation_fn(value)) or not wrap_as_validator
        except (ValueError, ValidationError):
            return False

    return wrapped


number_format_validator = create_validator(
    lambda x: isinstance(x, float) if x != 0 else isinstance(x, (int, float)), True
)

base64_format_validator = create_validator(lambda x: base64.b64encode(base64.b64decode(x, validate=True)) == x)

VALIDATOR_MAP: Dict[str, Callable] = {
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


def validate_type(schema_section: Dict[str, Any], data: Any) -> Optional[str]:
    schema_type: str = schema_section.get("type", "object")
    if not VALIDATOR_MAP[schema_type](data):
        an_articles = ["integer", "object", "array"]
        return VALIDATE_TYPE_ERROR.format(
            article="a" if schema_type not in an_articles else "an",
            type=schema_type,
            received=f'"{data}"' if isinstance(data, str) else data,
        )
    return None


def validate_format(schema_section: Dict[str, Any], data: Any) -> Optional[str]:
    schema_format: str = schema_section.get("format", "")
    if schema_format in VALIDATOR_MAP and not VALIDATOR_MAP[schema_format](data):
        example_values = {
            "byte": {"value": b"example", "article": "a"},
            "base64": {"value": b"ZXhhbXBsZQ==", "article": "a"},
            "date": {"value": '"2020-01-22"', "article": "a"},
            "date-time": {"value": '"2020-01-22 08:00"', "article": "a"},
            "double": {"value": "2.22", "article": "a"},
            "email": {"value": '"example@gmail.com"', "article": "an"},
            "float": {"value": "2.2", "article": "a"},
            "ipv4": {"value": '"192.0.2.235"', "article": "an"},
            "ipv6": {"value": '"2001:0db8:85a3:0000:0000:8a2e:0370:7334"', "article": "an"},
            "time": {"value": '"20:00:00"', "article": "a"},
            "uri": {"value": '"https://example.com/"', "article": "a"},
            "url": {"value": '"https://example.com/"', "article": "a"},
        }
        return VALIDATE_FORMAT_ERROR.format(
            format=schema_format,
            article=example_values[schema_format]["article"],  # type: ignore
            example=example_values[schema_format]["value"],  # type: ignore
            received=f'"{data}"',
        )
    return None


def pretty_print_list(_list: list) -> str:  # noqa
    if len(_list) == 1:
        return f'"{_list[0]}"'
    if len(_list) == 2:
        # No oxford comma
        return f'"{_list[0]}" or "{_list[1]}"'
    message = f'"{_list[0]}"'
    for index in range(1, len(_list) - 1):
        message += f', "{_list[index]}"'
    message += f', or "{_list[-1]}"'
    return message


def validate_enum(schema_section: Dict[str, Any], data: Any) -> Optional[str]:
    enum = schema_section.get("enum")
    if enum and data not in enum:
        return VALIDATE_ENUM_ERROR.format(expected=pretty_print_list(schema_section["enum"]), received=f'"{data}"')
    return None


def validate_pattern(schema_section: Dict[str, Any], data: str) -> Optional[str]:
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


def validate_multiple_of(schema_section: Dict[str, Any], data: Union[int, float]) -> Optional[str]:
    multiple = schema_section.get("multipleOf")
    if multiple and data % multiple != 0:
        return VALIDATE_MULTIPLE_OF_ERROR.format(data=data, multiple=multiple)
    return None


def validate_maximum(schema_section: Dict[str, Any], data: Union[int, float]) -> Optional[str]:
    maximum = schema_section.get("maximum")
    exclusive_maximum = schema_section.get("exclusiveMaximum")
    if maximum and exclusive_maximum and data >= maximum:
        return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum - 1)
    if maximum and not exclusive_maximum and data > maximum:
        return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum)
    return None


def validate_minimum(schema_section: Dict[str, Any], data: Union[int, float]) -> Optional[str]:
    minimum = schema_section.get("minimum")
    exclusive_minimum = schema_section.get("exclusiveMinimum")
    if minimum and exclusive_minimum and data <= minimum:
        return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum + 1)
    if minimum and not exclusive_minimum and data < minimum:
        return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum)
    return None


def validate_unique_items(schema_section: Dict[str, Any], data: List[Any]) -> Optional[str]:
    unique_items = schema_section.get("uniqueItems")
    if unique_items and len(set(data)) != len(data):
        return VALIDATE_UNIQUE_ITEMS_ERROR.format(data=data)
    # TODO: handle deep dictionary comparison - for lists of dicts
    return None


def validate_min_length(schema_section: Dict[str, Any], data: str) -> Optional[str]:
    min_length: Optional[int] = schema_section.get("minLength")
    if min_length and len(data) < min_length:
        return VALIDATE_MIN_LENGTH_ERROR.format(data=data, min_length=min_length)
    return None


def validate_max_length(schema_section: Dict[str, Any], data: str) -> Optional[str]:
    max_length: Optional[int] = schema_section.get("maxLength")
    if max_length and len(data) > max_length:
        return VALIDATE_MAX_LENGTH_ERROR.format(data=data, max_length=max_length)
    return None


def validate_min_items(schema_section: Dict[str, Any], data: list) -> Optional[str]:
    min_length: Optional[int] = schema_section.get("minItems")
    if min_length and len(data) < min_length:
        return VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=data, min_length=min_length)
    return None


def validate_max_items(schema_section: Dict[str, Any], data: list) -> Optional[str]:
    max_length: Optional[int] = schema_section.get("maxItems")
    if max_length and len(data) > max_length:
        return VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(data=data, max_length=max_length)
    return None


def validate_min_properties(schema_section: Dict[str, Any], data: dict) -> Optional[str]:
    min_properties: Optional[int] = schema_section.get("minProperties")
    if min_properties and len(data.keys()) < int(min_properties):
        return VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=data, min_length=min_properties)
    return None


def validate_max_properties(schema_section: Dict[str, Any], data: dict) -> Optional[str]:
    max_properties: Optional[int] = schema_section.get("maxProperties")
    if max_properties and len(data.keys()) > int(max_properties):
        return VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=data, max_length=max_properties)
    return None
