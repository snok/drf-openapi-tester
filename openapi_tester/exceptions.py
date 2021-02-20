""" Exceptions Module """


class DocumentationError(AssertionError):
    """
    Custom exception raised when package tests fail.
    """

    pass


class CaseError(DocumentationError):
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
