.. role:: python(code)
   :language: python

############################
OpenAPI Specification Tester
############################

This package provides a simple test-utility to test the integrity of your OpenAPI/Swagger documentation against actual API responses.

Package is currently under development, and only supports the testing of swagger documentation implemented in Django using drf_yasg_. The ambition for release 1.0.0 is to expand the current features to support testing any openapi specification, and to cut the dependence on Django tooling.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg


Installation
############

Install using pip:

.. code:: python

    pip install openapi-tester

Add 'openapi_tester' to your INSTALLED_APPS setting in ``settings.py``:

.. code:: python

   INSTALLED_APPS = [
      ...
      'drf_yasg',
   ]

Configuration
#############

The app currently requires two parameters.

**Path**: The path to your OpenAPI specification. Can be an url, or the path to your document.

**Case**: The case standard you wish to enforce for your documentation. Can be 'camelcase', 'snakecase', or None.

- `camelcase`__: Checks that your documentation is camelCased (default).

.. __: https://en.wikipedia.org/wiki/Camel_case

- `snakecase`__: Checks that your documentation is snake_cased.

.. __: https://en.wikipedia.org/wiki/Camel_case

- None: Doesn't check the documentation case standard.


**Example**

.. code:: python

    OPENAPI_TESTER_SETTINGS = {
        'PATH': '127.0.0.1:8080/swagger/?format=openapi',
        'CASE': 'camelcase'
    }


Example
#######

The OpenAPI tester should primarily be used to supplement your existing API tests.

The easiest way to implement it would be in a test where you're successfully retrieving a valid response from an endpoint.

An example might look like this:

.. code:: python

    from django.contrib.auth.models import User
    from rest_framework.test import APITestCase

    from openapi_tester import validate_specification


    class TestMyAPI(APITestCase):

        def setUp(self):
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)
            self.path = '/api/v1/cars'

        def test_get_200(self):
            """
            Verifies that a 200 is returned for a valid GET request to the /correct/ endpoint.
            """
            response = self.client.get(self.path + '/correct' /, headers={'Content-Type': 'application/json'})
            expected_response = [
                {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium', 'width': 'Very wide', 'length': '2 meters'},
                {'name': 'Volvo', 'color': 'Red', 'height': 'Medium', 'width': 'Not wide', 'length': '2 meters'},
                {'name': 'Tesla', 'color': 'black', 'height': 'Medium', 'width': 'Wide', 'length': '2 meters'},
            ]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # Test Swagger documentation
            validate_specification(response, 'GET', self.path + '/correct/')

See the demo project and tests folder for more examples.
