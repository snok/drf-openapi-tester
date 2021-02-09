""" Loaders Module """
import difflib
import json
import pathlib
import re
from json import dumps, loads
from typing import Callable, Dict, List, Optional, Union
from urllib.parse import ParseResult, urlparse

import yaml
from django.urls import Resolver404, resolve
from openapi_spec_validator import openapi_v2_spec_validator, openapi_v3_spec_validator

# noinspection PyProtectedMember
from prance.util.resolver import RefResolver

# noinspection PyProtectedMember
from prance.util.url import ResolutionError
from rest_framework.schemas.generators import EndpointEnumerator

from openapi_tester.constants import PARAMETER_CAPTURE_REGEX, UNDOCUMENTED_SCHEMA_SECTION_ERROR
from openapi_tester.exceptions import LoadingError, UndocumentedSchemaSectionError

from . import type_declarations as td


def handle_recursion_limit(schema: dict) -> Callable:
    """
    We are using a currying pattern to pass schema into the scope of the handler.
    """

    # noinspection PyUnusedLocal
    def handler(iteration: int, parse_result: ParseResult, recursions: tuple):  # pylint: disable=unused-argument
        fragment = parse_result.fragment
        keys = [key for key in fragment.split("/") if key]
        definition = schema
        for key in keys:
            definition = definition[key]
        return remove_recursive_ref(definition, fragment)

    return handler


def remove_recursive_ref(schema: dict, fragment: str) -> dict:
    """
    Iterates over a dictionary to look for pesky recursive $refs using the fragment identifier.
    """
    for key, value in schema.items():
        if isinstance(value, dict):
            if "$ref" in value.keys() and fragment in value["$ref"]:
                # TODO: use this value in the testing - to ignore some parts of the specs
                schema[key] = {"x-recursive-ref-replaced": True}
            else:
                schema[key] = remove_recursive_ref(schema[key], fragment)
    return schema


class BaseSchemaLoader:
    """
    Base class for OpenAPI schema loading classes.

    Contains a template of methods that are required from a loader class, and a range of helper methods for interacting
    with an OpenAPI schema.
    """

    base_path = "/"

    def __init__(self):
        super().__init__()
        self.schema: Optional[dict] = None

    def load_schema(self) -> dict:
        """
        Put logic required to load a schema and return it here.
        """
        raise NotImplementedError("The `load_schema` method has to be overwritten.")

    def get_schema(self) -> dict:
        """
        Returns OpenAPI schema.
        """
        if self.schema is None:
            self.set_schema(self.load_schema())
        return self.schema  # type: ignore

    def de_reference_schema(self, schema: dict) -> dict:
        try:
            url = schema["basePath"] if "basePath" in schema else self.base_path
            recursion_handler = handle_recursion_limit(schema)
            resolver = RefResolver(
                schema,
                recursion_limit_handler=recursion_handler,
                recursion_limit=10,
                url=url,
            )
            resolver.resolve_references()
            return resolver.specs
        except ResolutionError as e:
            raise LoadingError(e.args[0]) from e

    def normalize_schema_paths(self, schema: dict) -> Dict[str, dict]:
        normalized_paths: Dict[str, dict] = {}
        for key, value in schema["paths"].items():
            if "{" in key:
                normalized_paths[key] = value
            else:
                normalized_paths[self.parameterize_path(key)] = value
        return {**schema, "paths": normalized_paths}

    @staticmethod
    def validate_schema(schema: dict):
        if "openapi" in schema:
            validator = openapi_v3_spec_validator
        else:
            validator = openapi_v2_spec_validator
        validator.validate(schema)

    def set_schema(self, schema: dict) -> None:
        """
        Sets self.schema and self.original_schema.
        """
        de_referenced_schema = self.de_reference_schema(schema)
        self.validate_schema(de_referenced_schema)
        self.schema = self.normalize_schema_paths(de_referenced_schema)

    def parameterize_path(self, de_parameterized_path: str) -> str:
        """
        Returns the appropriate endpoint route.
        """
        path, resolved_path = self.resolve_path(de_parameterized_path)
        for parameter in list(re.findall(PARAMETER_CAPTURE_REGEX, path)):
            parameter_name = parameter.replace("{", "").replace("}", "")
            path = path.replace(resolved_path.kwargs[parameter_name], parameter_name)
        return path

    @staticmethod
    def get_endpoint_paths() -> List[str]:
        """
        Returns a list of endpoint paths.
        """
        return list({endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()})

    def resolve_path(self, endpoint_path: str) -> tuple:
        """
        Resolves a Django path.
        """

        url_object = urlparse(endpoint_path)
        parsed_path = url_object.path if url_object.path.endswith("/") else url_object.path + "/"
        if not parsed_path.startswith("/"):
            parsed_path = "/" + parsed_path
        for path in [parsed_path, parsed_path[:-1]]:
            try:
                resolved_route = resolve(path)
                for key, value in resolved_route.kwargs.items():
                    # Replacing kwarg values back into the string seems to be the simplest way of bypassing complex
                    # regex handling. However, its important not to freely use the .replace() function, as a
                    # {value} of `1` would also cause the `1` in api/v1/ to be replaced
                    var_index = path.rfind(str(value))
                    path = path[:var_index] + f"{{{key}}}" + path[var_index + len(str(value)) :]
                return path, resolved_route
            except Resolver404:
                continue
        paths = self.get_endpoint_paths()
        closest_matches = "".join(f"\n- {i}" for i in difflib.get_close_matches(endpoint_path, paths))
        if closest_matches:
            raise ValueError(
                f"Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}"
            )
        raise ValueError(f"Could not resolve path `{endpoint_path}`")

    @staticmethod
    def _get_key_value(schema: dict, key: str, error_addon: str = "") -> dict:
        """
        Indexes the OpenAPI schema by a given key. We expect all keys tried to be present in a working shema.
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

    def get_response_schema_section(self, response: td.Response) -> dict:
        """
        Fetches the response section of a schema, wrt. the route, method, status code, and schema version.

        :param response: DRF Response Instance
        :return dict
        """
        schema = self.get_schema()
        parameterized_path = self.parameterize_path(response.request["PATH_INFO"])
        paths_object = self._get_key_value(schema, "paths")

        pretty_routes = "\n\t• ".join(paths_object.keys())
        route_object = self._get_key_value(
            paths_object,
            parameterized_path,
            f"\n\nFor debugging purposes, other valid routes include: \n\n\t• {pretty_routes}",
        )

        str_methods = ", ".join(method.upper() for method in route_object.keys() if method.upper() != "PARAMETERS")
        method_object = self._get_key_value(
            route_object, response.request["REQUEST_METHOD"].lower(), f"\n\nAvailable methods include: {str_methods}."
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
        content_object = self._get_key_value(status_code_object, "content")
        json_object = self._get_key_value(content_object, "application/json")
        return self._get_key_value(json_object, "schema")


class DrfYasgSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema generated by drf_yasg.
    """

    def __init__(self) -> None:
        super().__init__()
        from drf_yasg.generators import OpenAPISchemaGenerator
        from drf_yasg.openapi import Info

        self.schema_generator = OpenAPISchemaGenerator(info=Info(title="", default_version=""))

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf-yasg and returns it as a dict.
        """
        odict_schema = self.schema_generator.get_schema(None, True)
        return loads(dumps(odict_schema.as_odict()))

    def get_path_prefix(self) -> str:
        """
        Returns the drf_yasg specified path prefix.

        Drf_yasg `cleans` schema paths by finding recurring path patterns,
        and cutting them out of the generated openapi schema.
        For example, `/api/v1/example` might then just become `/example`
        """

        return self.schema_generator.determine_path_prefix(self.get_endpoint_paths())

    def resolve_path(self, endpoint_path: str) -> tuple:
        de_parameterized_path, resolved_path = super().resolve_path(endpoint_path=endpoint_path)
        path_prefix = self.get_path_prefix()  # typically might be 'api/' or 'api/v1/'
        if path_prefix == "/":
            path_prefix = ""
        return de_parameterized_path[len(path_prefix) :], resolved_path


class DrfSpectacularSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema generated by drf_spectacular.
    """

    def __init__(self) -> None:
        super().__init__()
        from drf_spectacular.generators import SchemaGenerator

        self.schema_generator = SchemaGenerator()

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf_spectacular and returns it as a dict.
        """
        return loads(dumps(self.schema_generator.get_schema(None, True)))

    @staticmethod
    def get_path_prefix() -> str:
        """
        Returns the drf_spectacular specified path prefix.
        """
        from drf_spectacular.settings import spectacular_settings

        return spectacular_settings.SCHEMA_PATH_PREFIX

    def resolve_path(self, endpoint_path: str) -> tuple:
        de_parameterized_path, resolved_path = super().resolve_path(endpoint_path=endpoint_path)
        path_prefix = self.get_path_prefix()  # typically might be 'api/' or 'api/v1/'
        if path_prefix == "/":
            path_prefix = ""
        return de_parameterized_path[len(path_prefix) :], resolved_path


class StaticSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema from a static file.
    """

    def __init__(self, path: str):
        super().__init__()
        self.path = path if not isinstance(path, pathlib.PosixPath) else str(path)

    def load_schema(self) -> dict:
        """
        Loads a static OpenAPI schema from file, and parses it to a python dict.

        :return: Schema contents as a dict
        :raises: ImproperlyConfigured
        """
        with open(self.path) as file:
            content = file.read()
            return json.loads(content) if ".json" in self.path else yaml.load(content, Loader=yaml.FullLoader)
