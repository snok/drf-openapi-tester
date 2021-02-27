""" Loaders Module """
import difflib
import json
import pathlib
from json import dumps, loads
from typing import Callable, Dict, List, Optional, Tuple, cast
from urllib.parse import ParseResult, urlparse

import yaml
from django.urls import Resolver404, ResolverMatch, resolve
from django.utils.functional import cached_property
from openapi_spec_validator import openapi_v2_spec_validator, openapi_v3_spec_validator

# noinspection PyProtectedMember
from prance.util.resolver import RefResolver

# noinspection PyProtectedMember
from rest_framework.schemas.generators import BaseSchemaGenerator, EndpointEnumerator
from rest_framework.settings import api_settings

import openapi_tester.type_declarations as td


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
        return definition

    return handler


class BaseSchemaLoader:
    """
    Base class for OpenAPI schema loading classes.

    Contains a template of methods that are required from a loader class, and a range of helper methods for interacting
    with an OpenAPI schema.
    """

    base_path = "/"
    field_key_map: Dict[str, str]
    schema: Optional[dict] = None

    def __init__(self, field_key_map: Optional[Dict[str, str]] = None):
        super().__init__()
        self.schema: Optional[dict] = None
        self.field_key_map = field_key_map or {}

    def load_schema(self) -> dict:
        """
        Put logic required to load a schema and return it here.
        """
        raise NotImplementedError("The `load_schema` method has to be overwritten.")

    def get_schema(self) -> dict:
        """
        Returns OpenAPI schema.
        """
        if self.schema:
            return self.schema
        self.set_schema(self.load_schema())
        return self.get_schema()

    def de_reference_schema(self, schema: dict) -> dict:
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

    def normalize_schema_paths(self, schema: dict) -> Dict[str, dict]:
        normalized_paths: Dict[str, dict] = {}
        for key, value in schema["paths"].items():
            try:
                parameterized_path, _ = self.resolve_path(endpoint_path=key, method=list(value.keys())[0])
                normalized_paths[parameterized_path] = value
            except ValueError:
                normalized_paths[key] = value
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

    @cached_property
    def endpoints(self) -> List[str]:  # pylint: disable=no-self-use
        """
        Returns a list of endpoint paths.
        """
        return list({endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()})

    def resolve_path(self, endpoint_path: str, method: str) -> Tuple[str, ResolverMatch]:
        """
        Resolves a Django path.
        """
        url_object = urlparse(endpoint_path)
        parsed_path = url_object.path if url_object.path.endswith("/") else url_object.path + "/"
        if not parsed_path.startswith("/"):
            parsed_path = "/" + parsed_path
        for key, value in self.field_key_map.items():
            if value != "pk" and key in parsed_path:
                parsed_path = parsed_path.replace(f"{{{key}}}", value)
        for path in [parsed_path, parsed_path[:-1]]:
            try:
                resolved_route = resolve(path)
            except Resolver404:
                continue
            else:
                for key, value in resolved_route.kwargs.items():
                    index = path.rfind(str(value))
                    path = f"{path[:index]}{{{key}}}{path[index + len(str(value)):]}"
                if "{pk}" in path and api_settings.SCHEMA_COERCE_PATH_PK:
                    path, resolved_route = self.handle_pk_parameter(
                        resolved_route=resolved_route, path=path, method=method
                    )
                return path, resolved_route
        message = f"Could not resolve path `{endpoint_path}`."
        close_matches = difflib.get_close_matches(endpoint_path, self.endpoints)
        if close_matches:
            message += "\n\nDid you mean one of these?" + "\n- ".join(close_matches)
        raise ValueError(message)

    @staticmethod
    def handle_pk_parameter(resolved_route: ResolverMatch, path: str, method: str) -> Tuple[str, ResolverMatch]:
        """
        Handle the DRF conversion of params called {pk} into a named parameter based on Model field
        """
        coerced_path = BaseSchemaGenerator().coerce_path(
            path=path, method=method, view=cast(td.APIView, resolved_route.func)
        )
        pk_field_name = "".join(
            entry.replace("+ ", "") for entry in difflib.Differ().compare(path, coerced_path) if "+ " in entry
        )
        resolved_route.kwargs[pk_field_name] = resolved_route.kwargs["pk"]
        del resolved_route.kwargs["pk"]
        return coerced_path, resolved_route


class DrfYasgSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema generated by drf_yasg.
    """

    def __init__(self, field_key_map: Optional[Dict[str, str]] = None) -> None:
        super().__init__(field_key_map=field_key_map)
        from drf_yasg.generators import OpenAPISchemaGenerator
        from drf_yasg.openapi import Info

        self.schema_generator = OpenAPISchemaGenerator(info=Info(title="", default_version=""))

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf-yasg and returns it as a dict.
        """
        odict_schema = self.schema_generator.get_schema(None, True)
        return loads(dumps(odict_schema.as_odict()))

    def resolve_path(self, endpoint_path: str, method: str) -> Tuple[str, ResolverMatch]:
        de_parameterized_path, resolved_path = super().resolve_path(endpoint_path=endpoint_path, method=method)
        path_prefix = self.schema_generator.determine_path_prefix(self.endpoints)
        trim_length = len(path_prefix) if path_prefix != "/" else 0
        return de_parameterized_path[trim_length:], resolved_path


class DrfSpectacularSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema generated by drf_spectacular.
    """

    def __init__(self, field_key_map: Optional[Dict[str, str]] = None) -> None:
        super().__init__(field_key_map=field_key_map)
        from drf_spectacular.generators import SchemaGenerator

        self.schema_generator = SchemaGenerator()

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf_spectacular and returns it as a dict.
        """
        return loads(dumps(self.schema_generator.get_schema(public=True)))

    def resolve_path(self, endpoint_path: str, method: str) -> Tuple[str, ResolverMatch]:
        from drf_spectacular.settings import spectacular_settings

        de_parameterized_path, resolved_path = super().resolve_path(endpoint_path=endpoint_path, method=method)
        return (
            de_parameterized_path[len(spectacular_settings.SCHEMA_PATH_PREFIX) :],
            resolved_path,
        )


class StaticSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema from a static file.
    """

    def __init__(self, path: str, field_key_map: Optional[Dict[str, str]] = None):
        super().__init__(field_key_map=field_key_map)
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
