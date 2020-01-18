# test script
import os
import sys

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
            OPENAPI_TESTER_SETTINGS={'PATH': 'http://127.0.0.1:8080/swagger/?format=openapi', 'CASE': 'CAMELCASE'},
        )
        django.setup()

    # todo allow passing function from command line
    @staticmethod
    def test() -> None:
        """
        Run a function from the CS class.

        :return: whatever the specified CS class function returns
        """
        from openapi_tester import oat_settings
        from openapi_tester.tester import OpenAPITester, SwaggerBase

        t = OpenAPITester()

        e = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]

        t.swagger_documentation(response=e, method='get', path='/api/v1/cars/correct/')


# todo allow running all class function from command line, not just test
if __name__ == '__main__':
    test = Test().test()
