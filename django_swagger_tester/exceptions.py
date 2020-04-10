class SwaggerDocumentationError(Exception):
    """
    Custom exception raised when package tests fail.
    """

    pass


class CaseError(Exception):
    """
    Custom exception raised when items are not cased correctly.
    """

    pass


class OpenAPISchemaError(Exception):
    """
    Custom exception raised for invalid schema specifications.
    """

    pass
