from typing import Optional, Any


class SwaggerDocumentationError(Exception):
    """
    Custom exception raised when package tests fail.
    """

    def __init__(
        self, message: str, response: Any = None, schema: Optional[dict] = None, reference: str = '', hint: str = ''
    ) -> None:
        super(SwaggerDocumentationError, self).__init__(message)
        if schema is None:
            schema = {}
        self.message = message
        self.response = response
        self.schema = schema
        self.reference = reference
        self.hint = hint


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
