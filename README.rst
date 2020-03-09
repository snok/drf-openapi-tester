############################
Django Swagger Tester
############################

.. image:: https://img.shields.io/pypi/v/django-swagger-tester.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/pypi/pyversions/django-swagger-tester.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/pypi/djversions/django-swagger-tester.svg
    :target: https://pypi.python.org/pypi/django-swagger-tester

.. image:: https://codecov.io/gh/sondrelg/django-swagger-tester/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/sondrelg/django-swagger-tester

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

.. role:: python(code)
   :language: python

This package provides a simple test utility for testing the integrity of your OpenAPI/Swagger documentation.

The test utility has two main functions. First, the documentation is tested by ensuring that it matches the content of actual API responses, and secondly the package ensures that all documentation adheres to the case-type specified as standard, .e.g, camel case.

The package is currently under development.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg

************
Installation
************

Install using pip:

.. code:: bash

    pip install django-swagger-tester

*************
Configuration
*************

Add package settings to your ``settings.py``:

.. code-block:: python

    SWAGGER_TESTER = {
        'SCHEMA': 'dynamic',
        'CASE': 'camel case'
    }

**********
Parameters
**********

* :code:`SCHEMA`
        The type of schema you are using. Can either be :code:`dynamic` or :code:`static`.

    Default: `dynamic`

* :code:`CASE`
        The case standard you wish to enforce for your documentation. Needs to be one of the following:
            * :code:`camel case`
            * :code:`snake case`
            * :code:`pascal case`
            * :code:`kebab case`
            * :code:`None`

        Every key in your tested endpoint's schema will be verified as compliant or non-compliant according to the
        selected case, unless you specify :code:`None` to skip this feature.

    Default: :code:`camel case`

* :code:`PATH`
        The path to your OpenAPI specification.

    *This is not required if you're using a dynamic schema*.

|

********
Examples
********

Using drf_yasg_ for dynamic schema generation, your configuration might look like this:

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg

.. code:: python

    SWAGGER_TESTER = {
        'SCHEMA': 'dynamic',
        'CASE': 'camel case'
    }

While using, e.g., DRF_ for static schema generation, you would need to add the path to your generated schema:

.. _DRF: https://www.django-rest-framework.org/api-guide/schemas/

.. code:: python

    SWAGGER_TESTER = {
        'SCHEMA': 'dynamic',
        'CASE': 'camel case'
        'PATH': './swagger/schema.json'
    }

**************
Implementation
**************

The OpenAPI tester is best used for supplementing your existing API tests.

The easiest way to implement it, is by testing your schema after retrieving a valid response from an endpoint.

An example might look like this:

.. code:: python

    from django.contrib.auth.models import User
    from rest_framework.test import APITestCase

    from django_swagger_tester import validate_response


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
            validate_response(response, 'GET', self.path + '/correct/')

See the demo projects and tests folder for more examples.
