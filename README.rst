.. role:: python(code)
   :language: python

########################################
OpenAPI/Swagger specification tester
########################################

Provides a simple test-utility to test the integrity of your OpenAPI/Swagger documentation.

Package is currently under development, and only supports swagger documentation implemented in Django using drf_yasg_.

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

Example
#######

The OpenAPI tester should primarily be used to supplement your existing API tests.

The easiest way to implement it would be in a test where you're successfully retrieving a valid response from an endpoint.

An example might look like this:

.. code:: python

    from django.contrib.auth.models import User
    from django.urls import reverse
    from requests.models import Response
    from rest_framework.test import APITestCase
    from openapi_tester import validate_specification


    class TestMyAPI(APITestBase):

        def setUp(self):
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)
            self.path = '/api/v1/cars'

        def test_get_200(self):

            expected_response = [
                {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium', 'width': 'Very wide', 'length': '2 meters'},
                {'name': 'Volvo', 'color': 'Red', 'height': 'Medium', 'width': 'Not wide', 'length': '2 meters'},
                {'name': 'Tesla', 'color': 'black', 'height': 'Medium', 'width': 'Wide', 'length': '2 meters'},
            ]

            response = self.client.get(self.path + '/correct'/, headers={'Content-Type': 'application/json'})

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # Test Swagger documentation
            validate_specification(response, 'GET', self.path + '/correct/')
