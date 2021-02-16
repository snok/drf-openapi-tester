""" Exceptions Module """
import json
from typing import TYPE_CHECKING, Any, Optional

from openapi_tester.utils import sort_object

if TYPE_CHECKING:
    from openapi_tester.schema_tester import Instance


class DocumentationError(AssertionError):
    """
    Custom exception raised when package tests fail.
    """

    def __init__(
        self, message: str, instance: "Instance" = None, example: Any = None, hint: Optional[str] = None
    ) -> None:
        """
        :param message: The error message
        :param message: An optional Validator instance containing all required data to format an exception.
        :param example: Optional example override. Lets us provide custom examples for some custom exceptions.
        """
        from openapi_tester.schema_converter import SchemaToPythonConverter
        from openapi_tester.schema_tester import Instance

        if isinstance(instance, Instance):
            example = example or sort_object(SchemaToPythonConverter(instance.schema_section, with_faker=False).result)
            super().__init__(self.format_message(message, example, instance.data, instance.reference, hint))
        else:
            super().__init__(message)

    @staticmethod
    def format_message(message: str, example: Any, data: Any, reference: str, hint: Optional[str]) -> str:
        """
        Formats and returns a standardized error message for easy debugging.
        """
        expected = json.dumps(example).replace('"', "")
        try:
            received = json.dumps(data)
        except TypeError:
            received = str(data)

        return "".join(
            [
                f"{message}\n\n",
                f"Expected: {expected}\n\n",
                f"Received: {received}\n\n",
                f"Hint: {hint}\n\n" if hint else "",
                f"Sequence: {reference}\n" if reference else "",
            ]
        )


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
