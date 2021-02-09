""" Schema Tester """
import re
from dataclasses import dataclass
from functools import reduce
from typing import Any, Callable, Generator, List, Optional, Union, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.response import Response
from rest_framework.test import APITestCase

from openapi_tester import type_declarations as td
from openapi_tester.constants import (
    ANY_OF_ERROR,
    EXCESS_RESPONSE_KEY_ERROR,
    INVALID_PATTERN_ERROR,
    MISSING_RESPONSE_KEY_ERROR,
    NONE_ERROR,
    ONE_OF_ERROR,
    OPENAPI_FORMAT_EXAMPLES,
    OPENAPI_PYTHON_MAPPING,
    OPENAPI_TYPE_EXAMPLES,
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
    VALIDATE_RESPONSE_TYPE_ERROR,
    VALIDATE_TYPE_ERROR,
    VALIDATE_UNIQUE_ITEMS_ERROR,
)
from openapi_tester.exceptions import DocumentationError
from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from openapi_tester.utils import combine_sub_schemas, get_schema_type


@dataclass
class ValidationError:
    """
    Contains schema validation results.
    """

    message: str
    verbose: bool
    unit: "SchemaValidationUnit"
    example: Optional[Any] = None
    hint: Optional[str] = ""


@dataclass
class SchemaValidationUnit:
    """
    Contains all the data we need to validate an individual section of an OpenAPI schema.
    """

    schema_section: dict
    data: Any
    reference: str
    case_tester: Optional[Callable[[str], None]]
    ignore_case: Optional[List[str]]

    @property
    def validators(self) -> Generator:
        yield from [
            self._validate_enum,
            self._validate_openapi_type,
            self._validate_format,
            self._validate_pattern,
            self._validate_multiple_of,
            self._validate_min_and_max,
            self._validate_length,
            self._validate_unique_items,
            self._validate_array_length,
            self._validate_number_of_properties,
        ]

    @property
    def enum(self) -> Optional[List[str]]:
        return self.schema_section.get("enum")

    @property
    def pattern(self) -> Optional[str]:
        return self.schema_section.get("pattern")

    @property
    def format(self) -> Optional[str]:
        return self.schema_section.get("format")

    @property
    def schema_type(self) -> Optional[str]:
        return get_schema_type(self.schema_section)

    @property
    def multiple_of(self) -> Optional[Union[int, float]]:
        return self.schema_section.get("multipleOf")

    @property
    def minimum(self) -> Optional[Union[int, float]]:
        return self.schema_section.get("minimum")

    @property
    def maximum(self) -> Optional[Union[int, float]]:
        return self.schema_section.get("maximum")

    @property
    def exclusive_minimum(self) -> Optional[Union[int, float]]:
        return self.schema_section.get("exclusiveMinimum")

    @property
    def exclusive_maximum(self) -> Optional[Union[int, float]]:
        return self.schema_section.get("exclusiveMaximum")

    @property
    def unique_items(self) -> Optional[bool]:
        return self.schema_section.get("uniqueItems")

    @property
    def min_length(self) -> Optional[int]:
        return self.schema_section.get("minLength")

    @property
    def max_length(self) -> Optional[int]:
        return self.schema_section.get("maxLength")

    @property
    def min_items(self) -> Optional[int]:
        return self.schema_section.get("minItems")

    @property
    def max_items(self) -> Optional[int]:
        return self.schema_section.get("maxItems")

    @property
    def min_properties(self) -> Optional[int]:
        return self.schema_section.get("minProperties")

    @property
    def max_properties(self) -> Optional[int]:
        return self.schema_section.get("maxProperties")

    def _validate_enum(self) -> Optional[ValidationError]:
        if not self.enum or self.data in self.enum:
            return None
        return ValidationError(
            message=VALIDATE_ENUM_ERROR.format(enum=self.schema_section["enum"], received=str(self.data)),
            verbose=True,
            example=self.enum,
            unit=self,
        )

    def _validate_pattern(self) -> Optional[ValidationError]:
        if not self.pattern:
            return None
        try:
            compiled_pattern = re.compile(self.pattern)
        except re.error as e:
            raise DocumentationError(INVALID_PATTERN_ERROR.format(pattern=self.pattern)) from e
        if compiled_pattern.match(self.data):
            return None
        return ValidationError(
            message=VALIDATE_PATTERN_ERROR.format(data=self.data, pattern=self.pattern),
            verbose=True,
            example=self.pattern,
            unit=self,
        )

    def _validate_format(self) -> Optional[ValidationError]:
        if not self.format:
            return None
        valid = True
        if self.format in ["double", "float"]:
            valid = isinstance(self.data, float)
        elif self.format == "byte":
            valid = isinstance(self.data, bytes)
        elif self.format in ["date", "date-time"]:
            parser = parse_date if self.format == "date" else parse_datetime
            valid = parser(self.data) is not None
        if valid:
            return None
        return ValidationError(
            message=VALIDATE_FORMAT_ERROR.format(format=self.format),
            verbose=True,
            example=OPENAPI_FORMAT_EXAMPLES[self.format],
            unit=self,
        )

    def _validate_openapi_type(self) -> Optional[ValidationError]:
        valid = True
        if not self.schema_type:
            return None
        if self.schema_type in ["file", "string"]:
            valid = isinstance(self.data, (str, bytes))
        elif self.schema_type == "integer":
            valid = isinstance(self.data, int) and not isinstance(self.data, bool)
        elif self.schema_type == "number":
            valid = isinstance(self.data, (int, float)) and not isinstance(self.data, bool)
        elif self.schema_type == "object":
            valid = isinstance(self.data, dict)
        elif self.schema_type == "array":
            valid = isinstance(self.data, list)
        elif self.schema_type == "boolean":
            valid = isinstance(self.data, bool)
        if not valid:
            return ValidationError(
                message=VALIDATE_TYPE_ERROR.format(type=self.schema_type),
                verbose=True,
                example=OPENAPI_TYPE_EXAMPLES[self.schema_type],
                unit=self,
            )

    def _validate_multiple_of(self) -> Optional[ValidationError]:
        if self.multiple_of and self.data % self.multiple_of != 0:
            return ValidationError(
                message=VALIDATE_MULTIPLE_OF_ERROR.format(data=self.data, multiple=self.multiple_of),
                verbose=False,
                unit=self,
            )

    def _validate_min_and_max(self) -> Optional[ValidationError]:
        error = ""
        if self.minimum and self.exclusive_minimum and self.data <= self.minimum:
            error = VALIDATE_MINIMUM_ERROR.format(data=self.data, minimum=self.minimum + 1)
        if self.minimum and not self.exclusive_minimum and self.data < self.minimum:
            error = VALIDATE_MINIMUM_ERROR.format(data=self.data, minimum=self.minimum)
        if self.maximum and self.exclusive_maximum and self.data >= self.maximum:
            error = VALIDATE_MAXIMUM_ERROR.format(data=self.data, maximum=self.maximum - 1)
        if self.maximum and not self.exclusive_maximum and self.data > self.maximum:
            error = VALIDATE_MAXIMUM_ERROR.format(data=self.data, maximum=self.maximum)
        if error:
            return ValidationError(
                message=error,
                verbose=False,
                unit=self,
            )

    def _validate_unique_items(self) -> Optional[ValidationError]:
        if self.unique_items and len(set(self.data)) != len(self.data):
            return ValidationError(
                message=VALIDATE_UNIQUE_ITEMS_ERROR,
                verbose=False,
                unit=self,
            )
        # TODO: handle deep dictionary comparison - for lists of dicts
        return None

    def _validate_length(self) -> Optional[ValidationError]:
        error = ""
        if self.min_length and len(self.data) < self.min_length:
            error = VALIDATE_MIN_LENGTH_ERROR.format(data=self.data, min_length=self.min_length)
        if self.max_length and len(self.data) > self.max_length:
            error = VALIDATE_MAX_LENGTH_ERROR.format(data=self.data, max_length=self.max_length)
        if error:
            return ValidationError(
                message=error,
                verbose=False,
                unit=self,
            )

    def _validate_array_length(self) -> Optional[ValidationError]:
        error = ""
        if self.min_length and len(self.data) < self.min_length:
            error = VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=self.data, min_length=self.min_length)
        if self.max_length and len(self.data) > self.max_length:
            error = VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(data=self.data, max_length=self.max_length)
        if error:
            return ValidationError(
                message=error,
                verbose=False,
                unit=self,
            )

    def _validate_number_of_properties(self) -> Optional[ValidationError]:
        error = ""
        if self.min_properties and len(self.data) < self.min_properties:
            error = VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=self.data, min_length=self.min_properties)
        if self.max_properties and len(self.data) > self.max_properties:
            error = VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=self.data, max_length=self.max_properties)
        if error:
            return ValidationError(
                message=error,
                verbose=False,
                unit=self,
            )

    @property
    def is_nullable(self) -> bool:
        """
        Checks if the item is nullable.

        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/

        :return: whether or not the item is allowed to be None
        """
        openapi_schema_3_nullable = "nullable"
        swagger_2_nullable = "x-nullable"
        return any(
            nullable_key in self.schema_section and self.schema_section[nullable_key]
            for nullable_key in [openapi_schema_3_nullable, swagger_2_nullable]
        )


class SchemaTester:
    """ Schema Tester: this is the base class of the library. """

    loader: Union[StaticSchemaLoader, DrfSpectacularSchemaLoader, DrfYasgSchemaLoader]

    def __init__(
        self,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
        schema_file_path: Optional[str] = None,
    ) -> None:
        """
        Iterates through an OpenAPI schema object and API response to check that they match at every level.

        :param case_tester: An optional callable that validates schema and response keys
        :param ignore_case: An optional list of keys for the case_tester to ignore
        :schema_file_path: The file path to an OpenAPI yaml or json file. Only passed when using a static schema loader
        :raises: openapi_tester.exceptions.DocumentationError or ImproperlyConfigured
        """
        self.case_tester = case_tester
        self.ignore_case = ignore_case or []

        if schema_file_path is not None:
            self.loader = StaticSchemaLoader(schema_file_path)
        elif "drf_spectacular" in settings.INSTALLED_APPS:
            self.loader = DrfSpectacularSchemaLoader()
        elif "drf_yasg" in settings.INSTALLED_APPS:
            self.loader = DrfYasgSchemaLoader()
        else:
            raise ImproperlyConfigured("Unable to configure loader")

    def handle_all_of(self, unit: SchemaValidationUnit) -> None:
        unit.reference += ".allOf"
        unit.schema_section = {**unit.schema_section, **combine_sub_schemas(unit.schema_section.pop("allOf"))}
        self.test_schema_section(unit)

    def handle_one_of(self, unit: SchemaValidationUnit):
        unit.reference += ".oneOf"
        matches = 0
        for option in unit.schema_section["oneOf"]:
            try:
                unit.schema_section = option
                self.test_schema_section(unit)
                matches += 1
            except DocumentationError:
                continue
        if matches != 1:
            raise DocumentationError(ONE_OF_ERROR.format(matches=matches))

    def handle_any_of(self, unit: SchemaValidationUnit):
        unit.reference += ".anyOf"

        any_of: List[dict] = unit.schema_section.get("anyOf", [])
        combined_sub_schemas = map(
            lambda index: reduce(lambda x, y: combine_sub_schemas([x, y]), any_of[index:]), range(len(any_of))
        )

        for schema in [*any_of, *combined_sub_schemas]:
            try:
                unit.schema_section = schema
                self.test_schema_section(unit)
                return
            except DocumentationError:
                continue
        raise DocumentationError(ANY_OF_ERROR)

    def test_schema_section(self, unit: SchemaValidationUnit) -> None:
        """
        This method orchestrates the testing of a schema section
        """
        if unit.data is None:
            if unit.is_nullable:
                return
            raise DocumentationError(
                ValidationError(
                    message=NONE_ERROR.format(expected=OPENAPI_PYTHON_MAPPING[unit.schema_section.get("type", "")]),
                    verbose=True,
                    hint="Document the contents of the empty dictionary to match the response object.",
                    unit=unit,
                )
            )

        if "oneOf" in unit.schema_section:
            self.handle_one_of(unit)
            return
        if "allOf" in unit.schema_section:
            self.handle_all_of(unit)
            return
        if "anyOf" in unit.schema_section:
            self.handle_any_of(unit)
            return

        schema_section_type = get_schema_type(unit.schema_section)
        for validator in unit.validators:
            error = validator()
            if error:
                raise DocumentationError(error)

        if schema_section_type == "object":
            self.test_openapi_object(unit)
        elif schema_section_type == "array":
            self.test_openapi_array(unit)

    def _validate_key_casing(
        self, key: str, case_tester: Optional[Callable[[str], None]] = None, ignore_case: Optional[List[str]] = None
    ) -> None:
        tester = case_tester or getattr(self, "case_tester", None)
        ignore_case = [*self.ignore_case, *(ignore_case or [])]
        if tester and key not in ignore_case:
            tester(key)

    def test_openapi_object(self, unit: SchemaValidationUnit) -> None:
        """
        1. Validate that casing is correct for both response and schema
        2. Check if any required key is missing from the response
        3. Check if any response key is not in the schema
        4. Validate sub-schema/nested data
        """
        properties = unit.schema_section.get("properties", {})
        required_keys = unit.schema_section.get("required", [])
        response_keys = unit.data.keys()
        additional_properties: Optional[Union[bool, dict]] = unit.schema_section.get("additionalProperties")
        if not properties and isinstance(additional_properties, dict):
            properties = additional_properties
        for key in properties.keys():
            self._validate_key_casing(key, unit.case_tester, unit.ignore_case)
            if key in required_keys and key not in response_keys:
                unit.reference += f".object:key:{key}"
                raise DocumentationError(
                    ValidationError(
                        message=MISSING_RESPONSE_KEY_ERROR.format(missing_key=key),
                        verbose=True,
                        unit=unit,
                        hint="Remove the key from your OpenAPI docs, or include it in your API response.",
                    )
                )
        for key in response_keys:
            self._validate_key_casing(key, unit.case_tester, unit.ignore_case)
            key_in_additional_properties = isinstance(additional_properties, dict) and key in additional_properties
            additional_properties_allowed = additional_properties is True
            if key not in properties and not key_in_additional_properties and not additional_properties_allowed:
                unit.reference += f".object:key:{key}"
                raise DocumentationError(
                    ValidationError(
                        message=EXCESS_RESPONSE_KEY_ERROR.format(excess_key=key),
                        verbose=True,
                        hint="Remove the key from your API response, or include it in your OpenAPI docs.",
                        unit=unit,
                    )
                )

        reference = unit.reference
        for key, value in unit.data.items():
            unit.schema_section = properties[key]
            unit.reference = f"{reference}.object:key:{key}"
            unit.data = value
            self.test_schema_section(unit)

    def test_openapi_array(self, unit: SchemaValidationUnit) -> None:
        items = unit.schema_section["items"]  # the items keyword is required for arrays
        if unit.data and not items:
            unit.reference += ".array"
            raise DocumentationError(
                ValidationError(
                    message="Mismatched content. Response list contains data when the schema is empty.",
                    verbose=True,
                    unit=unit,
                    hint="Document the contents of the empty dictionary to match the response object.",
                )
            )

        reference = unit.reference
        for datum in unit.data:
            unit.reference = f"{reference}.array.item"
            unit.schema_section = items
            unit.data = datum
            self.test_schema_section(unit)

    def validate_response(
        self,
        response: td.Response,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ):
        """
        Verifies that an OpenAPI schema definition matches an API response.

        :param response: The HTTP response
        :param case_tester: Optional Callable that checks a string's casing
        :param ignore_case: List of strings to ignore when testing the case of response keys
        :raises: ``openapi_tester.exceptions.DocumentationError`` for inconsistencies in the API response and schema.
                 ``openapi_tester.exceptions.CaseError`` for case errors.
        """

        if not isinstance(response, Response):
            raise ValueError(VALIDATE_RESPONSE_TYPE_ERROR)

        response_schema = self.loader.get_response_schema_section(response)
        self.test_schema_section(
            unit=SchemaValidationUnit(
                schema_section=response_schema,
                data=response.json(),
                reference="init",
                case_tester=case_tester,
                ignore_case=ignore_case,
            )
        )

    def test_case(self) -> APITestCase:
        validate_response = self.validate_response

        def assert_response(
            response: td.Response,
            case_tester: Optional[Callable[[str], None]] = None,
            ignore_case: Optional[List[str]] = None,
        ) -> None:
            """
            Assert response matches the OpenAPI spec.
            """
            validate_response(response=response, case_tester=case_tester, ignore_case=ignore_case)

        return cast(td.OpenAPITestCase, type("OpenAPITestCase", (APITestCase,), {"assertResponse": assert_response}))
