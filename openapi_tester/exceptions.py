class OpenAPISchemaError(Exception):
    """
    Custom exception raised when package tests fail.
    """

    pass


class ImproperlyConfigured(Exception):
    """
    Settings are improperly configured.
    """

    # This is a duplicate of django's django.core.exceptions.ImproperlyConfigured exceptions.
    # Adding this, so it'll be easier to move away from Django as a dependency if needed.
    pass
