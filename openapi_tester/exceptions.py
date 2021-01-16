import json
from typing import Any

from openapi_tester.constants import OPENAPI_PYTHON_MAPPING


class DocumentationError(Exception):
    """
    Custom exception raised when package tests fail.
    """

    def __init__(
        self,
        message: str,
        response: Any,
        schema: dict,
        hint: str = '',
        reference: str = '',
    ) -> None:
        super().__init__(
            self.format(
                response=self._sort_data(response),
                example_item=self._sort_data(self.create_dict_from_schema(schema or {})),
                hint=hint,
                message=message,
                reference=reference,
            )
        )

    @staticmethod
    def _sort_data(data_object: Any) -> Any:
        if isinstance(data_object, dict):
            return dict(sorted(data_object.items()))
        elif isinstance(data_object, list):
            try:
                return sorted(data_object)
            except TypeError:
                return data_object

    def format(self, example_item: Any, response: Any, reference: str, message: str, hint: str) -> str:
        """
        Formats and returns a standardized error message for easy debugging.

        """
        message = [
            f'Error: {message}\n\n' f'Expected: {json.dumps(example_item)}\n\n',
            f'Received: {json.dumps(response)}\n\n',
        ]
        if hint:
            message += [f'Hint: {hint}\n\n']
        if reference:
            message += [
                f'Sequence: {reference}\n',
            ]
        return ''.join(message)

    def _iterate_schema_dict(self, schema_object: dict) -> dict:
        parsed_schema = {}
        if 'properties' in schema_object:
            properties = schema_object['properties']
        else:
            properties = {'': schema_object['additionalProperties']}
        for key, value in properties.items():
            if not isinstance(value, dict):
                raise ValueError()
            value_type = value['type']
            if 'example' in value:
                parsed_schema[key] = value['example']
            elif value_type == 'object':
                parsed_schema[key] = self._iterate_schema_dict(value)
            elif value_type == 'array':
                parsed_schema[key] = self._iterate_schema_list(value)  # type: ignore
            else:
                parsed_schema[key] = OPENAPI_PYTHON_MAPPING[value['type']]
        return parsed_schema

    def _iterate_schema_list(self, schema_array: dict) -> list:
        parsed_items = []
        raw_items = schema_array['items']
        items_type = raw_items['type']
        if items_type == 'object':
            parsed_items.append(self._iterate_schema_dict(raw_items))
        elif items_type == 'array':
            parsed_items.append(self._iterate_schema_list(raw_items))
        else:
            parsed_items.append(OPENAPI_PYTHON_MAPPING[raw_items['type']])
        return parsed_items

    def create_dict_from_schema(self, schema: dict) -> Any:
        """
        Converts an OpenAPI schema representation of a dict to dict.
        """
        schema_type = schema['type']
        if schema_type == 'array':
            return self._iterate_schema_list(schema)
        elif schema_type == 'object':
            return self._iterate_schema_dict(schema)
        else:
            return OPENAPI_PYTHON_MAPPING[schema_type]


class CaseError(Exception):
    """
    Custom exception raised when items are not cased correctly.
    """

    def __init__(self, key: str, case: str, expected: str) -> None:
        super().__init__(f'The response key `{key}` is not properly {case}. Expected value: {expected}')


class OpenAPISchemaError(Exception):
    """
    Custom exception raised for invalid schema specifications.
    """

    pass


class UndocumentedSchemaSectionError(Exception):
    """
    Custom exception raised when we cannot find a schema section.
    """

    pass
