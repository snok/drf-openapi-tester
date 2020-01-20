class SpecificationError(Exception):
    """
    Custom exception to clarify where the exception is being raised from.
    """

    pass


class ImproperlyConfigured(Exception):
    """
    Settings are improperly configured.
    """

    # This is a duplicate of django's django.core.exceptions.ImproperlyConfigured exceptions.
    # Adding this, so it'll be easier to move away from Django as a dependency if needed.
    pass
