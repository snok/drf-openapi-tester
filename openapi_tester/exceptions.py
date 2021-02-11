""" Exceptions Module """
import json
from typing import Any


class DocumentationError(AssertionError):
    """
    Custom exception raised when package tests fail.
    """

    def __init__(
        self,
        message: str,
        response: Any,
        schema: dict,
        hint: str = "",
        reference: str = "",
    ) -> None:
        from openapi_tester.schema_converter import SchemaToPythonConverter

        converted_schema = SchemaToPythonConverter(schema, with_faker=False).result
        super().__init__(
            self.format(
                response=self._sort_data(response),
                example_item=self._sort_data(converted_schema),
                hint=hint,
                message=message,
                reference=reference,
            )
        )

    @staticmethod
    def _sort_data(data_object: Any) -> Any:
        if isinstance(data_object, dict):
            return dict(sorted(data_object.items()))
        if isinstance(data_object, list):
            try:
                return sorted(data_object)
            except TypeError:
                pass
        return data_object

    @staticmethod
    def format(example_item: Any, response: Any, reference: str, message: str, hint: str) -> str:
        """
        Formats and returns a standardized error message for easy debugging.
        """
        example = json.dumps(example_item).replace('"', "")
        msg = [
            f"{message}\n\n",
            f"Expected: {example}\n\n",
            f"Received: {json.dumps(response)}\n\n",
        ]
        if hint:
            msg += [f"Hint: {hint}\n\n"]
        if reference:
            msg += [
                f"Sequence: {reference}\n",
            ]
        return "".join(msg)


class CaseError(AssertionError):
    """
    Custom exception raised when items are not cased correctly.
    """

    def __init__(self, key: str, case: str, expected: str) -> None:
        super().__init__(f"The response key `{key}` is not properly {case}. Expected value: {expected}")


class OpenAPISchemaError(Exception):
    """
    Custom exception raised for invalid schema specifications.
    """

    pass


class UndocumentedSchemaSectionError(OpenAPISchemaError):
    """
    Subset of OpenAPISchemaError, raised when we cannot find a single schema section.
    """

    pass
