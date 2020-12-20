from django.apps import AppConfig


class DjangoSwaggerTesterConfig(AppConfig):
    name = 'django_swagger_tester'

    def ready(self) -> None:
        """
        Runs after Django settings are initialized.

        If we don't run package validation here, we'll run into
        circular imports in the code using the settings object.
        """
        from django_swagger_tester.configuration import settings

        settings.validate()
