from django.apps import AppConfig

from response_tester.configuration import settings


class DjangoSwaggerTesterConfig(AppConfig):
    name = "response_tester"

    def ready(self) -> None:
        """
        Runs after Django settings are initialized.

        If we don't run package validation here, we'll run into
        circular imports in the code using the settings object.
        """

        settings.validate()
