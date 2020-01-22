import os.path

from .exceptions import ImproperlyConfigured


class Settings(object):
    def __init__(self) -> None:
        """
        Loads and validates the settings.
        """
        self.path = None
        self.case = 'camel case'
        self._load_django_settings()
        self._validate_settings()
        self.path = self.path.lower()

    def _load_django_settings(self) -> None:
        """
        Assigns self.path and self.case values from the users Django settings.
        """
        from django.conf import settings

        # Check that the settings are defined
        if not hasattr(settings, 'OPENAPI_TESTER'):
            raise ImproperlyConfigured('Please specify OPENAPI_TESTER in your settings.py')

        _settings = settings.OPENAPI_TESTER

        for setting, value in _settings.items():
            if hasattr(self, setting):
                setattr(self, setting, value)
            else:
                raise ImproperlyConfigured(f'`{setting}` is not a valid setting for the openapi-tester module')

    def _validate_settings(self) -> None:
        """
        Validates self.path and self.case after values have been populated from settings.
        """
        # Make sure path is specified
        if self.path is None:
            raise ImproperlyConfigured(f'`path` is a required setting for the openapi-tester module')

        # If it is specified, make sure it's correctly specified
        if not isinstance(self.path, str):
            raise ImproperlyConfigured('`path` needs to be a string')

        if 'http://' in self.path or 'https://' in self.path:
            pass  # We'll have to try and fetch the schema before we know if the url is correct
        else:
            if not os.path.isfile(self.path):
                raise ImproperlyConfigured(
                    f'The path "{self.path}" does not point to a valid file. '
                    'Make sure to point to the specification file or add a scheme to your url '
                    '(e.g., `http://`).'
                )

        supported_cases = ['camel case', 'snake case', None]

        if self.case not in supported_cases:
            raise ImproperlyConfigured(
                f'This package currently doesn\'t support a case called {self.case}.'
                f' Set case to `snake case` for snake_case, '
                f'`camel case` for camelCase, or None to skip case validation completely.'
            )
