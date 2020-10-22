from typing import Any, Optional


class SwaggerDocumentationError(Exception):
    """
    Custom exception raised when package tests fail.
    """

    def __init__(
        self,
        message: str,
        response: Any = None,
        schema: Optional[dict] = None,
        reference: str = '',
        response_hint: str = '',
        request_hint: str = '',
    ) -> None:
        super().__init__(message)
        if schema is None:
            schema = {}
        self.message = message
        self.response = response
        self.schema = schema
        self.reference = reference
        self.response_hint = response_hint
        self.request_hint = request_hint


class CaseError(Exception):
    """
    Custom exception raised when items are not cased correctly.
    """

    def __init__(self, key: str = '', case: str = '', origin: str = '') -> None:
        self.key = key
        self.case = case
        self.origin = origin


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
