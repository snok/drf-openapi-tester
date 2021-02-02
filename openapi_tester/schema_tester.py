import re
from typing import Any, Callable, Dict, KeysView, List, Optional, Union, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.response import Response
from rest_framework.test import APITestCase

from openapi_tester import type_declarations as td
from openapi_tester.constants import (
    EXCESS_RESPONSE_KEY_ERROR,
    INVALID_PATTERN_ERROR,
    MISSING_PROPERTY_KEY_ERROR,
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

        self.loader: Union[StaticSchemaLoader, DrfSpectacularSchemaLoader, DrfYasgSchemaLoader]
        if schema_file_path is not None:
            self.loader = StaticSchemaLoader(schema_file_path)
        elif "drf_spectacular" in settings.INSTALLED_APPS:
            self.loader = DrfSpectacularSchemaLoader()
        elif "drf_yasg" in settings.INSTALLED_APPS:
            self.loader = DrfYasgSchemaLoader()
        else:
            raise ImproperlyConfigured("No loader is configured.")

    @staticmethod
    def handle_all_of(**kwargs: dict) -> dict:
        properties: Dict[str, Any] = {}
        for entry in kwargs.pop("allOf"):
            for key, value in entry["properties"].items():
                if key in properties and isinstance(value, dict):
                    properties[key] = {**properties[key], **value}
                elif key in properties and isinstance(value, list):
                    properties[key] = [*properties[key], *value]
                else:
                    properties[key] = value
        return {**kwargs, "type": "object", "properties": properties}

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
                message=ONE_OF_ERROR.format(matches),
                response=data,
                schema=schema_section,
                reference=reference,
            )

    @staticmethod
    def _get_key_value(schema: dict, key: str, error_addon: str = "") -> dict:
        """
        Indexes schema by string variable.
        """
        try:
            return schema[key]
        except KeyError:
            raise UndocumentedSchemaSectionError(UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key, error_addon))

    @staticmethod
    def _get_status_code(schema: dict, status_code: Union[str, int], error_addon="") -> dict:
        """
        Indexes schema by string variable.
        """
        if str(status_code) in schema:
            return schema[str(status_code)]
        elif int(status_code) in schema:
            return schema[int(status_code)]
        raise UndocumentedSchemaSectionError(UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(status_code, error_addon))

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
        Indexes schema by url, HTTP method, and status code to get the schema section related to a specific response.

        :param response: DRF Response Instance
        :return Response schema
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

        if not enum:
            return None

        if data not in enum:
            return VALIDATE_ENUM_ERROR.format(enum=schema_section["enum"], received=str(data))

    @staticmethod
    def _validate_pattern(schema_section: dict, data: Any) -> Optional[str]:
        pattern = schema_section.get("pattern")
        if not pattern:
            return None
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise OpenAPISchemaError(INVALID_PATTERN_ERROR.format(pattern=pattern)) from e
        if not compiled_pattern.match(data):
            return VALIDATE_PATTERN_ERROR.format(data=data, pattern=pattern)

    @staticmethod
    def _validate_format(schema_section: dict, data: Any) -> Optional[str]:
        format = schema_section.get("format")
        if not format:
            return None

        valid = True
        if format in ["double", "float"]:
            valid = isinstance(data, float)
        elif format == "byte":
            valid = isinstance(data, bytes)
        elif format == "date":
            try:
                result = parse_date(data)
                valid = result is not None
            except ValueError:
                valid = False
        elif format == "date-time":
            try:
                result = parse_datetime(data)
                valid = result is not None
            except ValueError:
                valid = False
        if not valid:
            return VALIDATE_FORMAT_ERROR.format(expected=schema_section["format"], received=str(data))

    def _validate_openapi_type(self, schema_section: dict, data: Any) -> Optional[str]:
        valid = True
        schema_type = schema_section.get("type")
        if not schema_type:
            return None
        if schema_type in ["string", "file"]:
            valid = isinstance(data, (str, bytes))
        elif schema_type == "integer":
            valid = isinstance(data, int)
        elif schema_type == "number":
            valid = isinstance(data, (int, float))
        elif schema_type == "object":
            valid = isinstance(data, dict)
        elif schema_type == "array":
            valid = isinstance(data, list)
        if data is None:
            valid = self.is_nullable(schema_section)
        if not valid:
            return VALIDATE_TYPE_ERROR.format(
                expected=OPENAPI_PYTHON_MAPPING[schema_type], received=type(data).__name__
            )

    @staticmethod
    def _validate_multiple_of(schema_section: dict, data: Any) -> Optional[str]:
        multiple = schema_section.get("multipleOf")
        if multiple is None:
            return None
        if data % multiple != 0:
            return VALIDATE_MULTIPLE_OF_ERROR.format(data=data, multiple=multiple)

    @staticmethod
    def _validate_min_and_max(schema_section: dict, data: Any) -> Optional[str]:
        minimum = schema_section.get("minimum")
        if minimum is not None:
            exclusive_minimum = schema_section.get("exclusiveMinimum")
            if not exclusive_minimum:
                if data < minimum:
                    return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum)
            else:
                if data <= minimum:
                    return VALIDATE_MINIMUM_ERROR.format(data=data, minimum=minimum + 1)

        maximum = schema_section.get("maximum")
        if maximum is not None:
            exclusive_maximum = schema_section.get("exclusiveMaximum")
            if not exclusive_maximum:
                if data > maximum:
                    return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum)
            else:
                if data >= maximum:
                    return VALIDATE_MAXIMUM_ERROR.format(data=data, maximum=maximum - 1)

    @staticmethod
    def _validate_length(schema_section: dict, data: str) -> Optional[str]:
        min_length = schema_section.get("minLength")
        if min_length is not None and len(data) < min_length:
            return VALIDATE_MIN_LENGTH_ERROR.format(data=data, min_length=min_length)

        max_length = schema_section.get("maxLength")
        if max_length is not None and len(data) > max_length:
            return VALIDATE_MAX_LENGTH_ERROR.format(data=data, max_length=max_length)

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
        else:
            if "allOf" in schema_section:
                merged_schema = self.handle_all_of(**schema_section)
                schema_section = merged_schema

            validators = [
                self._validate_openapi_type,
                self._validate_format,
                self._validate_pattern,
                self._validate_enum,
                self._validate_multiple_of,
                self._validate_min_and_max,
                self._validate_length,
            ]

            for validator in validators:
                error = validator(schema_section, data)
                if isinstance(error, str):
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

        properties = schema_section.get("properties", {})
        required_keys = schema_section.get("required", [])
        response_keys = list(data.keys())

        # Checks and assumptions made below:

        # 1. In the definitions above, we assume the `properties` section of the schema describes all keys,
        # meaning we should never find response keys missing from this set.
        # 2. Similarly, required keys must be a subset of properties; we should never find required keys that
        # are not described in the properties.
        # 3. Lastly, the response should contain *at minimum* all required keys, and keys outside of this
        # section should exist in the properties
        # 4. As a bonus check, we check the case of all keys

        message, hint = "", ""
        for required_key in required_keys:

            if required_key not in response_keys:
                hint = "Remove the key from your OpenAPI docs, or include it in your API response."
                message = MISSING_RESPONSE_KEY_ERROR.format(missing_key=required_key)
            else:
                # Pop keys here, so we can iterate through remaining keys afterwards; this lets us
                # efficiently verify that no excess keys exist the the properties definition
                response_keys.remove(required_key)

            if required_key not in properties:
                hint = "Document the property in your OpenAPI docs, or remove it from required."
                message = MISSING_PROPERTY_KEY_ERROR.format(missing_key=required_key)

        for remaining_response_key in response_keys:
            if remaining_response_key not in properties:
                hint = "Remove the key from your API response, or include it in your OpenAPI docs."
                message = EXCESS_RESPONSE_KEY_ERROR.format(excess_key=remaining_response_key)

        if message:
            raise DocumentationError(
                message=message,
                response=data,
                schema=schema_section,
                reference=reference,
                hint=hint,
            )

        # Now that we know all response keys and required keys match the property keys
        # both in value and formatting, we can check the case for all properties in one go
        for key in properties:
            self._validate_key_casing(key, case_tester, ignore_case)

            # And if it's contained in the response, we further validate
            # the responses values against the schema definitions
            if key in data:
                schema_value = properties[key]
                response_value = data[key]
                self.test_schema_section(
                    schema_section=schema_value,
                    data=response_value,
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
