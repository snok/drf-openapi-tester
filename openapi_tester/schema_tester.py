import re
from functools import reduce
from typing import Any, Callable, Dict, KeysView, List, Optional, Union, cast

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
    OPENAPI_PYTHON_MAPPING,
    UNDOCUMENTED_SCHEMA_SECTION_ERROR,
    VALIDATE_ENUM_ERROR,
    VALIDATE_FORMAT_ERROR,
    VALIDATE_MAX_LENGTH_ERROR,
    VALIDATE_MAXIMUM_ERROR,
    VALIDATE_MIN_LENGTH_ERROR,
    VALIDATE_MINIMUM_ERROR,
    VALIDATE_MULTIPLE_OF_ERROR,
    VALIDATE_PATTERN_ERROR,
    VALIDATE_RESPONSE_TYPE_ERROR,
    VALIDATE_TYPE_ERROR,
)
from openapi_tester.exceptions import DocumentationError, OpenAPISchemaError, UndocumentedSchemaSectionError
from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader


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
            raise ImproperlyConfigured("No loader is configured.")

    @staticmethod
    def combine_sub_schemas(schemas: List[dict]) -> Dict[str, Any]:
        array_schemas = [schema for schema in schemas if schema.get("type") == "array"]
        if array_schemas:
            items_lists = [schema.get("items", []) for schema in array_schemas]
            return {"type": "array", "items": [item for item_list in items_lists for item in item_list]}
        properties: Dict[str, Any] = {}
        required = []
        for entry in schemas:
            required.extend(entry.get("required", []))
            for key, value in entry.get("properties", {}).items():
                if key in properties and isinstance(value, dict):
                    properties[key] = {**properties[key], **value}
                elif key in properties and isinstance(value, list):
                    properties[key] = [*properties[key], *value]
                else:
                    properties[key] = value
        return {"type": "object", "required": required, "properties": properties}

    def handle_all_of(self, **kwargs: Any) -> Dict[str, Any]:
        all_of: List[dict] = kwargs.pop("allOf", [])
        return {**kwargs, **self.combine_sub_schemas(all_of)}

    def handle_one_of(
        self,
        schema_section: dict,
        data: Any,
        reference: str,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ):
        matches = 0
        for option in schema_section["oneOf"]:
            try:
                self.test_schema_section(
                    schema_section=option,
                    data=data,
                    reference=reference,
                    case_tester=case_tester,
                    ignore_case=ignore_case,
                )
                matches += 1
            except DocumentationError:
                continue
        if matches != 1:
            raise DocumentationError(
                message=ONE_OF_ERROR.format(matches=matches),
                response=data,
                schema=schema_section,
                reference=reference,
            )

    def handle_any_of(
        self,
        schema_section: dict,
        data: Any,
        reference: str,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ):
        any_of: List[Dict[str, Any]] = schema_section.get("anyOf", [])
        combined_sub_schemas: List[Dict[str, Any]] = []

        for index in range(len(any_of)):
            # we are reducing a slice of the any_of list from current index to list end

            combined_sub_schemas.append(reduce(lambda x, y: self.combine_sub_schemas([x, y]), any_of[index:]))

        valid = False
        for schema in [*any_of, *reversed(combined_sub_schemas)]:
            try:
                self.test_schema_section(
                    schema_section=schema,
                    data=data,
                    reference=reference,
                    case_tester=case_tester,
                    ignore_case=ignore_case,
                )
                valid = True
                break
            except DocumentationError:
                continue
        if not valid:
            raise DocumentationError(
                message=ANY_OF_ERROR.format(schemas=str([*any_of, *reversed(combined_sub_schemas)])),
                response=data,
                schema=schema_section,
                reference=reference,
                hint="",
            )

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
        elif int(status_code) in schema:
            return schema[int(status_code)]
        raise UndocumentedSchemaSectionError(
            UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key=status_code, error_addon=error_addon)
        )

    @staticmethod
    def _route_error_text_addon(paths: KeysView) -> str:
        route_error_text = ""
        pretty_routes = "\n\t• ".join(paths)
        route_error_text += f"\n\nFor debugging purposes, other valid routes include: \n\n\t• {pretty_routes}"
        return route_error_text

    @staticmethod
    def _method_error_text_addon(methods: KeysView) -> str:
        str_methods = ", ".join(method.upper() for method in methods if method.upper() != "PARAMETERS")
        return f"\n\nAvailable methods include: {str_methods}."

    @staticmethod
    def _responses_error_text_addon(status_code: Union[int, str], response_status_codes: KeysView) -> str:
        keys = ", ".join([str(key) for key in response_status_codes])
        return f"\n\nUndocumented status code: {status_code}.\n\nDocumented responses include: {keys}. "

    def get_response_schema_section(self, response: td.Response) -> dict:
        """
        :param response: DRF Response Instance
        :return dict
        """
        schema = self.loader.get_schema()
        parameterized_path = self.loader.parameterize_path(response.request["PATH_INFO"])
        paths_object = self._get_key_value(schema, "paths")
        route_object = self._get_key_value(
            paths_object,
            parameterized_path,
            self._route_error_text_addon(paths_object.keys()),
        )
        method_object = self._get_key_value(
            route_object, response.request["REQUEST_METHOD"].lower(), self._method_error_text_addon(route_object.keys())
        )
        responses_object = self._get_key_value(method_object, "responses")
        status_code_object = self._get_status_code(
            responses_object,
            response.status_code,
            self._responses_error_text_addon(response.status_code, responses_object.keys()),
        )
        if "openapi" not in schema:
            # openapi 2.0, i.e. "swagger" has a different structure than openapi 3.0 status sub-schemas
            return self._get_key_value(status_code_object, "schema")
        content_object = self._get_key_value(status_code_object, "content")
        json_object = self._get_key_value(content_object, "application/json")
        return self._get_key_value(json_object, "schema")

    @staticmethod
    def is_nullable(schema_item: dict) -> bool:
        """
        Checks if the item is nullable.

        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/

        :param schema_item: schema item
        :return: whether or not the item can be None
        """
        openapi_schema_3_nullable = "nullable"
        swagger_2_nullable = "x-nullable"
        return any(
            nullable_key in schema_item and schema_item[nullable_key]
            for nullable_key in [openapi_schema_3_nullable, swagger_2_nullable]
        )

    def _validate_key_casing(
        self, key: str, case_tester: Optional[Callable[[str], None]] = None, ignore_case: Optional[List[str]] = None
    ) -> None:
        tester = case_tester or getattr(self, "case_tester", None)
        ignore_case = [*self.ignore_case, *(ignore_case or [])]
        if tester and key not in ignore_case:
            tester(key)

    @staticmethod
    def _validate_enum(schema_section: dict, data: Any) -> Optional[str]:
        enum = schema_section.get("enum")
        if enum and data not in enum:
            return VALIDATE_ENUM_ERROR.format(enum=schema_section["enum"], received=str(data))
        return None

    @staticmethod
    def _validate_pattern(schema_section: dict, data: Any) -> Optional[str]:
        pattern = schema_section.get("pattern")
        if not pattern:
            return None
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise OpenAPISchemaError(INVALID_PATTERN_ERROR.format(pattern=pattern)) from e
        return None if compiled_pattern.match(data) else VALIDATE_PATTERN_ERROR.format(data=data, pattern=pattern)

    @staticmethod
    def _validate_format(schema_section: dict, data: Any) -> Optional[str]:
        valid = True
        schema_format = schema_section.get("format")
        if schema_format in ["double", "float"]:
            valid = isinstance(data, float)
        elif schema_format == "byte":
            valid = isinstance(data, bytes)
        elif schema_format in ["date", "date-time"]:
            parser = parse_date if schema_format == "date" else parse_datetime
            try:
                result = parser(data)
                valid = result is not None
            except ValueError:
                valid = False
        return None if valid else VALIDATE_FORMAT_ERROR.format(expected=schema_section["format"], received=str(data))

    @staticmethod
    def _validate_openapi_type(schema_section: dict, data: Any) -> Optional[str]:
        valid = True
        schema_type: Optional[str] = schema_section.get("type")
        if not schema_type and "properties" in schema_section:
            schema_type = "object"
        if not schema_type:
            return None
        if schema_type in ["file", "string"]:
            valid = isinstance(data, (str, bytes))
        elif schema_type == "integer":
            valid = isinstance(data, int)
        elif schema_type == "number":
            valid = isinstance(data, (int, float))
        elif schema_type == "object":
            valid = isinstance(data, dict)
        elif schema_type == "array":
            valid = isinstance(data, list)
        return (
            None
            if valid
            else VALIDATE_TYPE_ERROR.format(expected=OPENAPI_PYTHON_MAPPING[schema_type], received=type(data).__name__)
        )

    @staticmethod
    def _validate_multiple_of(schema_section: dict, data: Any) -> Optional[str]:
        multiple = schema_section.get("multipleOf")
        if multiple and data % multiple != 0:
            return VALIDATE_MULTIPLE_OF_ERROR.format(data=data, multiple=multiple)
        return None

    @staticmethod
    def _validate_min_and_max(schema_section: dict, data: Any) -> Optional[str]:
        minimum = schema_section.get("minimum")
        maximum = schema_section.get("maximum")
        exclusive_minimum = schema_section.get("exclusiveMinimum")
        exclusive_maximum = schema_section.get("exclusiveMaximum")
        if minimum and exclusive_minimum and data <= minimum:
            return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum + 1)
        if minimum and not exclusive_minimum and data < minimum:
            return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum)
        if maximum and exclusive_maximum and data >= maximum:
            return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum - 1)
        if maximum and not exclusive_maximum and data > maximum:
            return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum)
        return None

    @staticmethod
    def _validate_length(schema_section: dict, data: str) -> Optional[str]:
        min_length: Optional[int] = schema_section.get("minLength")
        max_length: Optional[int] = schema_section.get("maxLength")
        if min_length and len(data) < min_length:
            return VALIDATE_MIN_LENGTH_ERROR.format(data=data, min_length=min_length)
        if max_length and len(data) > max_length:
            return VALIDATE_MAX_LENGTH_ERROR.format(data=data, max_length=max_length)
        return None

    def test_schema_section(
        self,
        schema_section: dict,
        data: Any,
        reference: str = "",
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ) -> None:
        """
        This method orchestrates the testing of a schema section
        """
        schema_section_type = schema_section.get("type")
        if not schema_section_type and "properties" in schema_section:
            schema_section_type = "object"
        if schema_section_type is None or (data is None and self.is_nullable(schema_section)):
            # If there`s no type, any response is permitted so we return early
            # If data is None and nullable, we also return early
            return
        if data is None:
            raise DocumentationError(
                message=NONE_ERROR.format(expected=OPENAPI_PYTHON_MAPPING[schema_section_type]),
                response=data,
                schema=schema_section,
                reference=reference,
                hint="Document the contents of the empty dictionary to match the response object.",
            )

        if "oneOf" in schema_section:
            self.handle_one_of(
                schema_section=schema_section,
                data=data,
                reference=reference,
                case_tester=case_tester,
                ignore_case=ignore_case,
            )
        elif "anyOf" in schema_section:
            self.handle_any_of(
                schema_section=schema_section,
                data=data,
                reference=reference,
                case_tester=case_tester,
                ignore_case=ignore_case,
            )
        else:
            if "allOf" in schema_section:
                merged_schema = self.handle_all_of(**schema_section)
                schema_section = merged_schema

            validators = [
                self._validate_enum,
                self._validate_openapi_type,
                self._validate_format,
                self._validate_pattern,
                self._validate_multiple_of,
                self._validate_min_and_max,
                self._validate_length,
            ]
            for validator in validators:
                error = validator(schema_section, data)
                if error:
                    raise DocumentationError(message=error, response=data, schema=schema_section, reference=reference)

            if schema_section_type == "object":
                self._test_openapi_type_object(
                    schema_section=schema_section,
                    data=data,
                    reference=reference,
                    case_tester=case_tester,
                    ignore_case=ignore_case,
                )
            elif schema_section_type == "array":
                self._test_openapi_type_array(
                    schema_section=schema_section,
                    data=data,
                    reference=reference,
                    case_tester=case_tester,
                    ignore_case=ignore_case,
                )

    def _test_openapi_type_object(
        self,
        schema_section: dict,
        data: dict,
        reference: str,
        case_tester: Optional[Callable[[str], None]],
        ignore_case: Optional[List[str]],
    ) -> None:
        """
        1. Validate that casing is correct for both response and schema
        2. Check if any required key is missing from the response
        3. Check if any response key is not in the schema
        4. Validate sub-schema/nested data
        """

        properties = schema_section.get("properties", {})
        required_keys = schema_section.get("required", [])
        response_keys = data.keys()
        for key in properties.keys():
            self._validate_key_casing(key, case_tester, ignore_case)
            if key in required_keys and key not in response_keys:
                raise DocumentationError(
                    message=MISSING_RESPONSE_KEY_ERROR.format(missing_key=key),
                    hint="Remove the key from your OpenAPI docs, or include it in your API response.",
                    response=data,
                    schema=schema_section,
                    reference=reference,
                )
        for key in response_keys:
            self._validate_key_casing(key, case_tester, ignore_case)
            if key not in properties:
                raise DocumentationError(
                    message=EXCESS_RESPONSE_KEY_ERROR.format(excess_key=key),
                    hint="Remove the key from your API response, or include it in your OpenAPI docs.",
                    response=data,
                    schema=schema_section,
                    reference=reference,
                )
        for key, value in data.items():
            self.test_schema_section(
                schema_section=properties[key],
                data=value,
                reference=f"{reference}.dict:key:{key}",
                case_tester=case_tester,
                ignore_case=ignore_case,
            )

    def _test_openapi_type_array(
        self,
        schema_section: dict,
        data: dict,
        reference: str,
        case_tester: Optional[Callable[[str], None]],
        ignore_case: Optional[List[str]],
    ) -> None:
        items = schema_section["items"]

        error = ""
        if items is None and data is not None:
            error = "Mismatched content. Response list contains data when the schema is empty."
        elif data is None and not self.is_nullable(schema_section):
            error = NONE_ERROR.format(expected="list")
        elif data is None:
            return

        if error:
            raise DocumentationError(
                message=error,
                response=data,
                schema=schema_section,
                reference=reference,
                hint="Document the contents of the empty dictionary to match the response object.",
            )

        for datum in data:
            self.test_schema_section(
                schema_section=items,
                data=datum,
                reference=f"{reference}.list",
                case_tester=case_tester,
                ignore_case=ignore_case,
            )

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

        response_schema = self.get_response_schema_section(response)
        self.test_schema_section(
            schema_section=response_schema,
            data=response.json(),
            reference="init",
            case_tester=case_tester,
            ignore_case=ignore_case,
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
