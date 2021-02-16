""" Schema Tester """  # pylint: disable=R0401
from functools import reduce
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response

from openapi_tester import type_declarations as td
from openapi_tester.constants import (
    INIT_ERROR,
    OPENAPI_PYTHON_MAPPING,
    UNDOCUMENTED_SCHEMA_SECTION_ERROR,
    VALIDATE_ANY_OF_ERROR,
    VALIDATE_EXCESS_RESPONSE_KEY_ERROR,
    VALIDATE_MISSING_RESPONSE_KEY_ERROR,
    VALIDATE_NONE_ERROR,
    VALIDATE_ONE_OF_ERROR,
    VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR,
)
from openapi_tester.exceptions import DocumentationError, UndocumentedSchemaSectionError
from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from openapi_tester.utils import combine_sub_schemas, get_schema_type
from openapi_tester.validators import default_validators


class Instance:
    """
    Contains all state we need for a single invocation of validate_response.
    """

    def __init__(  # pylint: disable=R0913
        self,
        data: Any,
        reference: str,
        schema_section: dict,
        version: td.schema_versions,
        custom_validators: List[Callable],
        ignore_case: Optional[List[str]],
        case_tester: Optional[Callable[[str], None]],
    ):
        self.data = data
        self.version = version
        self.reference = reference
        self.case_tester = case_tester
        self.ignore_case = ignore_case
        self.schema_section = schema_section
        self.custom_validators = custom_validators

    @property
    def validators(self) -> Generator:
        yield from default_validators + self.custom_validators

    @property
    def schema_type(self):
        return get_schema_type(self.schema_section)

    @property
    def nullable(self) -> bool:
        """
        Checks if the item is nullable.
        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/
        :return: whether or not the item is allowed to be None
        """
        nullable_key = "x-nullable" if self.version == 20 else "nullable"
        return nullable_key in self.schema_section and self.schema_section[nullable_key]


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
        Defines the base settings for all validation calls to the schema tester instance.

        :param case_tester: An optional callable that validates schema and response keys
        :param ignore_case: An optional list of keys for the case_tester to ignore
        :schema_file_path: The file path to an OpenAPI yaml or json file. Only passed when using a static schema loader
        :raises: ImproperlyConfigured
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

    def get_response_schema_section(self, response: td.Response, version: td.schema_versions) -> Dict[str, Any]:
        """
        Fetches the response section of a schema, wrt. the route, method, status code, and schema version.

        :param response: DRF Response Instance
        :param version: The OpenAPI/Swagger schema version
        :returns: Response section of the schema relevant to the response given.
        """
        response_method = response.request["REQUEST_METHOD"].lower()
        parameterized_path = self.loader.parameterize_path(response.request["PATH_INFO"])
        paths_object = self._get_key_value(self.loader.get_schema(), "paths")

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
        if str(response.status_code) in responses_object:
            status_code_object = responses_object[str(response.status_code)]
        elif int(response.status_code) in responses_object:
            status_code_object = responses_object[int(response.status_code)]
        else:
            raise UndocumentedSchemaSectionError(
                UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(
                    key=response.status_code,
                    error_addon=f"\n\nUndocumented status code: {response.status_code}.\n\n"
                    f"Documented responses include: {keys}. ",
                )
            )

        if version == 20:
            # Swagger 2.0 has a different structure than OpenAPI 3.0
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

    def handle_all_of(self, instance: Instance) -> None:
        """
        Handles allOf referencing.

        See https://swagger.io/docs/specification/data-models/oneof-anyof-allof-not/#allof
        """
        instance.reference += ".allOf"
        instance.schema_section = {
            **instance.schema_section,
            **combine_sub_schemas(instance.schema_section.pop("allOf")),
        }
        self.test_schema_section(instance)

    def handle_one_of(self, instance: Instance):
        """
        Handles oneOf referencing.

        See https://swagger.io/docs/specification/data-models/oneof-anyof-allof-not/#oneof
        """
        instance.reference += ".oneOf"
        matches = 0
        for option in instance.schema_section["oneOf"]:
            try:
                instance.schema_section = option
                self.test_schema_section(instance)
                matches += 1
            except DocumentationError:
                continue
        if matches != 1:
            raise DocumentationError(VALIDATE_ONE_OF_ERROR.format(matches=matches))

    def handle_any_of(self, instance: Instance):
        """
        Handles anyOf referencing.

        See https://swagger.io/docs/specification/data-models/oneof-anyof-allof-not/#anyof
        """
        instance.reference += ".anyOf"
        any_of: List[dict] = instance.schema_section.get("anyOf", [])
        combined_sub_schemas = map(
            lambda index: reduce(lambda x, y: combine_sub_schemas([x, y]), any_of[index:]),
            range(len(any_of)),
        )
        for schema in [*any_of, *combined_sub_schemas]:
            try:
                instance.schema_section = schema
                self.test_schema_section(instance)
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

    def test_schema_section(self, instance: Instance) -> None:
        """
        This method orchestrates the testing of a schema section
        """
        if instance.data is None:
            if instance.nullable:
                # If data is None and nullable, we return early
                return
            raise DocumentationError(
                message=VALIDATE_NONE_ERROR.format(expected=OPENAPI_PYTHON_MAPPING[instance.schema_type]),
                instance=instance,
                hint="Document the contents of the empty dictionary to match the response object.",
            )
        if "oneOf" in instance.schema_section:
            self.handle_one_of(instance)
            return
        if "allOf" in instance.schema_section:
            self.handle_all_of(instance)
            return
        if "anyOf" in instance.schema_section:
            self.handle_any_of(instance)
            return

        for validator in instance.validators:
            validator(instance)

        if instance.schema_type == "object":
            self.test_openapi_object(instance)
        elif instance.schema_type == "array":
            self.test_openapi_array(instance)

    def test_openapi_object(self, instance: Instance) -> None:
        """
        1. Validate that casing is correct for both response and schema
        2. Check if any required key is missing from the response
        3. Check if any response key is not in the schema
        4. Validate sub-schema/nested data
        """
        response_keys = instance.data.keys()
        additional_properties = instance.schema_section.get("additionalProperties")
        properties = instance.schema_section.get("properties", {})
        write_only_properties = (
            [key for key in properties.keys() if properties[key].get("writeOnly")] if properties else []
        )
        required_properties = [
            key for key in instance.schema_section.get("required", []) if key not in write_only_properties
        ]

        property_keys: Iterable[str] = []
        if properties:
            property_keys = properties.keys()
        elif isinstance(additional_properties, dict):
            property_keys = additional_properties.keys()

        for key in property_keys:
            self._validate_key_casing(key, instance.case_tester, instance.ignore_case)
            if key in required_properties and key not in response_keys:
                instance.reference += f".object:key:{key}"
                raise DocumentationError(
                    message=VALIDATE_MISSING_RESPONSE_KEY_ERROR.format(missing_key=key),
                    hint="Remove the key from your OpenAPI docs, or include it in your API response.",
                    instance=instance,
                )
        for key in response_keys:
            self._validate_key_casing(key, instance.case_tester, instance.ignore_case)
            key_in_additional_properties = isinstance(additional_properties, dict) and key in additional_properties
            additional_properties_allowed = additional_properties is True
            if key not in properties and not key_in_additional_properties and not additional_properties_allowed:
                instance.reference += f".object:key:{key}"
                raise DocumentationError(
                    message=VALIDATE_EXCESS_RESPONSE_KEY_ERROR.format(excess_key=key),
                    hint="Remove the key from your API response, or include it in your OpenAPI docs.",
                    instance=instance,
                )
            if key in write_only_properties:
                instance.reference += f".object:key:{key}"
                raise DocumentationError(
                    message=VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR.format(write_only_key=key),
                    hint="Remove the key from your API response, or remove the `WriteOnly` restriction.",
                    instance=instance,
                )
        for key, value in instance.data.items():
            instance.data = value
            instance.schema_section = properties[key]
            instance.reference += f".object:key:{key}"
            self.test_schema_section(instance)

    def test_openapi_array(self, instance) -> None:
        for datum in instance.data:
            instance.data = datum
            instance.schema_section = instance.schema_section["items"]
            instance.reference += ".array.item"
            self.test_schema_section(instance)

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
        if isinstance(self.loader.schema, dict) and "swagger" in self.loader.schema:
            version = 20
        else:
            version = 30

        response_schema = self.get_response_schema_section(response, version)  # type: ignore

        validators = self.custom_validators
        if isinstance(custom_validators, list):
            validators += custom_validators

        instance = Instance(
            schema_section=response_schema,
            data=response.json(),
            reference="init",
            version=version,  # type: ignore
            case_tester=case_tester,
            ignore_case=ignore_case,
            custom_validators=validators,
        )
        self.test_schema_section(instance)
