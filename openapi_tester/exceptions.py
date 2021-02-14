""" Exceptions Module """
import json
from typing import Any

from openapi_tester.utils import sort_object


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
                response=sort_object(response),
                example_item=sort_object(converted_schema),
                hint=hint,
                message=message,
                reference=reference,
            )
        )

    @staticmethod
    def format(example_item: Any, response: Any, reference: str, message: str, hint: str) -> str:
        """
        Formats and returns a standardized error message for easy debugging.
        """

        expected = json.dumps(example_item).replace('"', "")
        try:
            received = json.dumps(response)
        except TypeError:
            received = str(response)

        msg = [
            f"{message}\n\n",
            f"Expected: {expected}\n\n",
            f"Received: {received}\n\n",
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
