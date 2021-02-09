""" Exceptions Module """
import json
from typing import Any, Union

from . import type_declarations as td


class DocumentationError(AssertionError):
    """
    Custom exception raised when package tests fail, with output displaying received/expected data.
    """

    def __init__(self, error: Union[td.ValidationError, str]) -> None:
        from openapi_tester.schema_converter import SchemaToPythonConverter

        if isinstance(error, str):
            super().__init__(error)
            return  # this is redundant but helps mypy

        if not error.verbose:
            super().__init__(error.message)

        example_item = error.example or SchemaToPythonConverter(error.unit.schema_section, with_faker=False).result
        super().__init__(
            self.format(
                response=self._sort_data(error.unit.data),
                example_item=self._sort_data(example_item),
                hint=error.hint or "",
                message=error.message,
                reference=error.unit.reference,
            )
        )

    @staticmethod
    def _sort_data(data_object: Any) -> Any:
        """
        Sorts data so that expected and received objects align.
        """
        if isinstance(data_object, dict):
            return dict(sorted(data_object.items()))
        if isinstance(data_object, list):
            try:
                return sorted(data_object)
            except TypeError:
                return data_object
        return data_object

    @staticmethod
    def format(example_item: Any, response: Any, reference: str, message: str, hint: str) -> str:
        """
        Formats and returns a standardized error message for easy debugging.
        """
        msg = [
            f"{message}\n\n",
            f"Expected: {json.dumps(example_item)}\n\n",
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


class LoadingError(Exception):
    """
    Custom exception raised when we fail to load a schema.
    """

    pass


class UndocumentedSchemaSectionError(LoadingError):
    """
    Custom exception raised when we cannot find a schema section.
    """

    pass
