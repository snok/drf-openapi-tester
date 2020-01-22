# flake8: noqa
import django
from django.conf import settings


class Test:
    def __init__(self) -> None:
        """
        Initialize 'django' and settings.
        Without this you'll just get errors if you try to run any of the CS class functions since no database is configured.
        """
        settings.configure(
            ENVIRONMENT='dev',
            DEBUG=True,
            ROOT_URLCONF='demo_project.urls',
            SECRET_KEY='test-key',
            INSTALLED_APPS=('django.contrib.auth', 'django.contrib.contenttypes', 'openapi_tester'),
            DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3',}},
            OPENAPI_TESTER={'path': 'http://127.0.0.1:8080/swagger/?format=openapi', 'case': 'camel case'},
        )
        django.setup()

    # todo allow passing function from command line
    @staticmethod
    def test() -> None:
        """
        Run a function from the CS class.
        :return: whatever the specified CS class function returns
        """
        from openapi_tester import validate_schema

        e = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
        ]

        validate_schema(response=e, method='get', endpoint_url='/api/v1/cars/correct/')


# todo allow running all class function from command line, not just test
if __name__ == '__main__':
    test = Test().test()
