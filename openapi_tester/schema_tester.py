""" Schema Tester """  # pylint: disable=R0401
import re
from enum import Enum
from functools import reduce
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.response import Response

from openapi_tester import type_declarations as td
from openapi_tester.constants import (
    INIT_ERROR,
    INVALID_PATTERN_ERROR,
    OPENAPI_FORMAT_EXAMPLES,
    OPENAPI_PYTHON_MAPPING,
    UNDOCUMENTED_SCHEMA_SECTION_ERROR,
    VALIDATE_ANY_OF_ERROR,
    VALIDATE_ENUM_ERROR,
    VALIDATE_EXCESS_RESPONSE_KEY_ERROR,
    VALIDATE_FORMAT_ERROR,
    VALIDATE_MAX_ARRAY_LENGTH_ERROR,
    VALIDATE_MAX_LENGTH_ERROR,
    VALIDATE_MAXIMUM_ERROR,
    VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR,
    VALIDATE_MIN_ARRAY_LENGTH_ERROR,
    VALIDATE_MIN_LENGTH_ERROR,
    VALIDATE_MINIMUM_ERROR,
    VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR,
    VALIDATE_MISSING_RESPONSE_KEY_ERROR,
    VALIDATE_MULTIPLE_OF_ERROR,
    VALIDATE_NONE_ERROR,
    VALIDATE_ONE_OF_ERROR,
    VALIDATE_PATTERN_ERROR,
    VALIDATE_TYPE_ERROR,
    VALIDATE_UNIQUE_ITEMS_ERROR,
    VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR,
)
from openapi_tester.exceptions import DocumentationError, UndocumentedSchemaSectionError
from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from openapi_tester.utils import combine_sub_schemas


class SchemaVersions(Enum):
    """ Contains all possible supported schema versions. """

    SWAGGER2: int = 20
    OPENAPI30: int = 30
    OPENAPI31: int = 31


class OpenAPIProperties:  # pylint: disable=R0904
    """
    Contains all OpenAPI data types, formats, and other properties.
    """

    def __init__(self, schema_section: dict, version: int):
        self.schema_section = schema_section
        self.version = version

    @property
    def properties(self) -> Optional[dict]:
        return self.schema_section.get("properties")

    @property
    def write_only_properties(self) -> list:
        if self.properties:
            return [key for key in self.properties.keys() if self.properties[key].get("writeOnly")]
        return []

    @property
    def required_properties(self) -> Optional[list]:
        return [key for key in self.schema_section.get("required", []) if key not in self.write_only_properties]

    @property
    def additional_properties(self) -> Optional[Union[bool, dict]]:
        return self.schema_section.get("additionalProperties")

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
        if "type" in self.schema_section:
            return self.schema_section["type"]
        if "properties" in self.schema_section or "additionalProperties" in self.schema_section:
            return "object"
        return None

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

    @property
    def nullable(self) -> bool:
        """
        Checks if the item is nullable.
        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/
        :return: whether or not the item is allowed to be None
        """
        nullable_key = "x-nullable" if self.version == SchemaVersions.SWAGGER2 else "nullable"
        return nullable_key in self.schema_section and self.schema_section[nullable_key]


class Validator(OpenAPIProperties):
    """
    Contains all the data we need to validate an individual section of an OpenAPI schema.
    """

    def __init__(  # pylint: disable=R0913
        self,
        data: Any,
        reference: str,
        schema_section: dict,
        version: int,
        custom_validators: List[Callable],
        ignore_case: Optional[List[str]],
        case_tester: Optional[Callable[[str], None]],
    ):
        super().__init__(schema_section, version)
        self.data = data
        self.reference = reference
        self.custom_validators = custom_validators
        self.ignore_case = ignore_case
        self.case_tester = case_tester

    def __dict__(self):
        return {
            "data": self.data,
            "reference": self.reference,
            "custom_validators": self.custom_validators,
            "ignore_case": self.ignore_case,
            "case_tester": self.case_tester,
            "schema_section": self.schema_section,
        }

    @property
    def validators(self) -> Generator:
        yield from [
            self.validate_enum,
            self.validate_openapi_type,
            self.validate_format,
            self.validate_pattern,
            self.validate_multiple_of,
            self.validate_min_and_max,
            self.validate_length,
            self.validate_unique_items,
            self.validate_array_length,
            self.validate_number_of_properties,
        ] + self.custom_validators

    def validate_enum(self) -> None:
        if self.enum and self.data not in self.enum:
            raise DocumentationError(
                message=VALIDATE_ENUM_ERROR.format(enum=self.schema_section["enum"]), example=self.enum, unit=self
            )

    def validate_pattern(self) -> None:
        if self.pattern:
            try:
                compiled_pattern = re.compile(self.pattern)
            except re.error as e:
                raise DocumentationError(INVALID_PATTERN_ERROR.format(pattern=self.pattern)) from e
            if not compiled_pattern.match(self.data):
                raise DocumentationError(
                    message=VALIDATE_PATTERN_ERROR.format(data=self.data, pattern=self.pattern),
                    example=self.pattern,
                    unit=self,
                )

    def validate_format(self) -> None:
        if self.format:
            valid = True
            if self.format in ["double", "float"]:
                valid = isinstance(self.data, float)
            elif self.format == "byte":
                valid = isinstance(self.data, bytes)
            elif self.format in ["date", "date-time"]:
                parser = parse_date if self.format == "date" else parse_datetime
                valid = parser(self.data) is not None
            if not valid:
                raise DocumentationError(
                    message=VALIDATE_FORMAT_ERROR.format(format=self.format),
                    example=OPENAPI_FORMAT_EXAMPLES[self.format],
                    unit=self,
                )

    def validate_openapi_type(self) -> None:
        if self.schema_type:
            valid = True
            if self.schema_type in ["file", "string"]:
                valid = isinstance(self.data, (str, bytes))
            elif self.schema_type == "boolean":
                valid = isinstance(self.data, bool)
            elif self.schema_type == "integer":
                valid = isinstance(self.data, int) and not isinstance(self.data, bool)
            elif self.schema_type == "number":
                valid = isinstance(self.data, (int, float)) and not isinstance(self.data, bool)
            elif self.schema_type == "object":
                valid = isinstance(self.data, dict)
            elif self.schema_type == "array":
                valid = isinstance(self.data, list)
            if not valid:
                raise DocumentationError(message=VALIDATE_TYPE_ERROR.format(type=self.schema_type), unit=self)

    def validate_multiple_of(self) -> None:
        if self.multiple_of and self.data % self.multiple_of != 0:
            error = VALIDATE_MULTIPLE_OF_ERROR.format(data=self.data, multiple=self.multiple_of)
            raise DocumentationError(message=error)

    def validate_min_and_max(self) -> None:
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
            raise DocumentationError(message=error)

    def validate_unique_items(self) -> None:
        if self.unique_items and len(set(self.data)) != len(self.data):
            raise DocumentationError(
                message=VALIDATE_UNIQUE_ITEMS_ERROR,
            )
        # TODO: handle deep dictionary comparison - for lists of dicts

    def validate_length(self) -> None:
        error = ""
        if self.min_length and len(self.data) < self.min_length:
            error = VALIDATE_MIN_LENGTH_ERROR.format(data=self.data, min_length=self.min_length)
        if self.max_length and len(self.data) > self.max_length:
            error = VALIDATE_MAX_LENGTH_ERROR.format(data=self.data, max_length=self.max_length)
        if error:
            raise DocumentationError(message=error)

    def validate_array_length(self) -> None:
        error = ""
        if self.min_length and len(self.data) < self.min_length:
            error = VALIDATE_MIN_ARRAY_LENGTH_ERROR.format(data=self.data, min_length=self.min_length)
        if self.max_length and len(self.data) > self.max_length:
            error = VALIDATE_MAX_ARRAY_LENGTH_ERROR.format(data=self.data, max_length=self.max_length)
        if error:
            raise DocumentationError(message=error)

    def validate_number_of_properties(self) -> None:
        error = ""
        if self.min_properties and len(self.data) < self.min_properties:
            error = VALIDATE_MINIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=self.data, min_length=self.min_properties)
        if self.max_properties and len(self.data) > self.max_properties:
            error = VALIDATE_MAXIMUM_NUMBER_OF_PROPERTIES_ERROR.format(data=self.data, max_length=self.max_properties)
        if error:
            raise DocumentationError(message=error)


class SchemaTester:
    """ Schema Tester: this is the base class of the library. """

    loader: Union[StaticSchemaLoader, DrfSpectacularSchemaLoader, DrfYasgSchemaLoader]

    def __init__(
        self,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
        schema_file_path: Optional[str] = None,
        custom_validators: Optional[List[Callable]] = None,
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
        self.custom_validators: List[Callable] = custom_validators or []

        if schema_file_path is not None:
            self.loader = StaticSchemaLoader(schema_file_path)
        elif "drf_spectacular" in settings.INSTALLED_APPS:
            self.loader = DrfSpectacularSchemaLoader()
        elif "drf_yasg" in settings.INSTALLED_APPS:
            self.loader = DrfYasgSchemaLoader()
        else:
            raise ImproperlyConfigured(INIT_ERROR)

    @staticmethod
    def _get_key_value(schema: dict, key: str, error_addon: str = "") -> dict:
        """
        Returns the value of a given key
        """
        try:
            return schema[key]
        except KeyError as e:
            raise UndocumentedSchemaSectionError(
                UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key=key, error_addon=error_addon)
            ) from e

    @staticmethod
    def _get_status_code(schema: dict, status_code: Union[str, int], error_addon: str = "") -> dict:
        """
        Returns the status code section of a schema, handles both str and int status codes
        """
        if str(status_code) in schema:
            return schema[str(status_code)]
        if int(status_code) in schema:
            return schema[int(status_code)]
        raise UndocumentedSchemaSectionError(
            UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key=status_code, error_addon=error_addon)
        )

    def get_response_schema_section(self, response: td.Response) -> Dict[str, Any]:
        """
        Fetches the response section of a schema, wrt. the route, method, status code, and schema version.

        :param response: DRF Response Instance
        :return dict
        """
        schema = self.loader.get_schema()
        response_method = response.request["REQUEST_METHOD"].lower()
        parameterized_path = self.loader.parameterize_path(response.request["PATH_INFO"])
        paths_object = self._get_key_value(schema, "paths")

        pretty_routes = "\n\t• ".join(paths_object.keys())
        route_object = self._get_key_value(
            paths_object,
            parameterized_path,
            f"\n\nValid routes include: \n\n\t• {pretty_routes}",
        )

        str_methods = ", ".join(method.upper() for method in route_object.keys() if method.upper() != "PARAMETERS")
        method_object = self._get_key_value(
            route_object,
            response_method,
            f"\n\nAvailable methods include: {str_methods}.",
        )

        responses_object = self._get_key_value(method_object, "responses")
        keys = ", ".join(str(key) for key in responses_object.keys())
        status_code_object = self._get_status_code(
            responses_object,
            response.status_code,
            f"\n\nUndocumented status code: {response.status_code}.\n\nDocumented responses include: {keys}. ",
        )

        if "openapi" not in schema:
            # openapi 2.0, i.e. "swagger" has a different structure than openapi 3.0 status sub-schemas
            return self._get_key_value(status_code_object, "schema")
        content_object = self._get_key_value(
            status_code_object,
            "content",
            f"No content documented for method: {response_method}, path: {parameterized_path}",
        )
        json_object = self._get_key_value(
            content_object,
            "application/json",
            f"no `application/json` responses documented for method: {response_method}, path: {parameterized_path}",
        )
        return self._get_key_value(json_object, "schema")

    def handle_all_of(self, unit: Validator) -> None:
        unit.reference += ".allOf"
        unit.schema_section = {**unit.schema_section, **combine_sub_schemas(unit.schema_section.pop("allOf"))}
        self.test_schema_section(unit)

    def handle_one_of(self, unit: Validator):
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
            raise DocumentationError(VALIDATE_ONE_OF_ERROR.format(matches=matches))

    def handle_any_of(self, unit: Validator):
        unit.reference += ".anyOf"
        any_of: List[dict] = unit.schema_section.get("anyOf", [])
        combined_sub_schemas = map(
            lambda index: reduce(lambda x, y: combine_sub_schemas([x, y]), any_of[index:]),
            range(len(any_of)),
        )
        for schema in [*any_of, *combined_sub_schemas]:
            try:
                unit.schema_section = schema
                self.test_schema_section(unit)
                return
            except DocumentationError:
                continue
        raise DocumentationError(VALIDATE_ANY_OF_ERROR)

    def _validate_key_casing(
        self,
        key: str,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ) -> None:
        tester = case_tester or getattr(self, "case_tester", None)
        ignore_case = [*self.ignore_case, *(ignore_case or [])]
        if tester and key not in ignore_case:
            tester(key)

    def test_schema_section(self, unit: Validator) -> None:
        """
        This method orchestrates the testing of a schema section
        """
        if unit.data is None:
            if unit.nullable:
                # If data is None and nullable, we return early
                return
            raise DocumentationError(
                message=VALIDATE_NONE_ERROR.format(expected=OPENAPI_PYTHON_MAPPING[unit.schema_type]),  # type: ignore
                unit=unit,
                hint="Document the contents of the empty dictionary to match the response object.",
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

        for validator in unit.validators:
            validator()

        if unit.schema_type == "object":
            self.test_openapi_object(unit)
        elif unit.schema_type == "array":
            self.test_openapi_array(unit)

    def test_openapi_object(self, unit) -> None:
        """
        1. Validate that casing is correct for both response and schema
        2. Check if any required key is missing from the response
        3. Check if any response key is not in the schema
        4. Validate sub-schema/nested data
        """
        response_keys = unit.data.keys()
        property_keys = unit.properties.keys() if unit.properties else []
        if not unit.properties and isinstance(unit.additional_properties, dict):
            property_keys = unit.additional_properties.keys()
        for key in property_keys:
            self._validate_key_casing(key, unit.case_tester, unit.ignore_case)
            if key in unit.required_keys and key not in response_keys:
                unit.reference += f".object:key:{key}"
                raise DocumentationError(
                    message=VALIDATE_MISSING_RESPONSE_KEY_ERROR.format(missing_key=key),
                    hint="Remove the key from your OpenAPI docs, or include it in your API response.",
                    unit=unit,
                )
        for key in response_keys:
            self._validate_key_casing(key, unit.case_tester, unit.ignore_case)
            key_in_additional_properties = (
                isinstance(unit.additional_properties, dict) and key in unit.additional_properties
            )
            additional_properties_allowed = unit.additional_properties is True
            if key not in unit.properties and not key_in_additional_properties and not additional_properties_allowed:
                unit.reference += f".object:key:{key}"
                raise DocumentationError(
                    message=VALIDATE_EXCESS_RESPONSE_KEY_ERROR.format(excess_key=key),
                    hint="Remove the key from your API response, or include it in your OpenAPI docs.",
                    unit=unit,
                )
            if key in unit.write_only_properties:
                unit.reference += f".object:key:{key}"
                raise DocumentationError(
                    message=VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR.format(write_only_key=key),
                    hint="Remove the key from your API response, or remove the `WriteOnly` restriction.",
                    unit=unit,
                )
        for key, value in unit.data.items():
            unit.data = value
            unit.schema_section = unit.properties[key]
            unit.reference += (f".object:key:{key}",)
            self.test_schema_section(unit)

    def test_openapi_array(self, unit) -> None:
        for datum in unit.data:
            unit.data = datum
            unit.schema_section = unit.schema_section["items"]
            unit.reference += ".array.item"
            self.test_schema_section(unit)

    def validate_response(
        self,
        response: Response,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
        custom_validators: Optional[List[Callable]] = None,
    ):
        """
        Verifies that an OpenAPI schema definition matches an API response.

        :param response: The HTTP response
        :param case_tester: Optional Callable that checks a string's casing
        :param ignore_case: List of strings to ignore when testing the case of response keys
        :param custom_validators: Optional list of extra validators to run on schema elements.
        :raises: ``openapi_tester.exceptions.DocumentationError`` for inconsistencies in the API response and schema.
                 ``openapi_tester.exceptions.CaseError`` for case errors.
        """
        response_schema = self.get_response_schema_section(response)

        if isinstance(self.loader.schema, dict) and "swagger" in self.loader.schema:
            version = SchemaVersions.SWAGGER2
        else:
            version = SchemaVersions.OPENAPI30

        validators = self.custom_validators
        if isinstance(custom_validators, list):
            validators += custom_validators

        unit = Validator(
            schema_section=response_schema,
            data=response.json(),
            reference="init",
            version=version,  # type: ignore
            case_tester=case_tester,
            ignore_case=ignore_case,
            custom_validators=validators,
        )
        self.test_schema_section(unit)
