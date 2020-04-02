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

|

This package provides a simple test utility for testing the integrity of your OpenAPI/Swagger documentation. The package has three main functions:

**Ensuring correct response documentation**

This might be obvious, but given that you can have several HTTP methods per endpoint (GET, PUT, POST, DELETE, ...), and that you can have several responses per *method* (200, 400, 401, 404, 5XX), response documentation usually ends up being the majority of swagger documentation in a project.

The primary goal of this package is to provide a simple utility to *ensure* that your response documentation is 1:1 with your actual responses. The utility checks every attribute of both responses and response documentation, recursively.

This is currently supported for swagger documentation implemented using `drf_yasg`_'s schema_view, or rendering of static schemas.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg

**2. Testing Input Documentation**

Let you validate your request body examples against your input serializers.

This is currently under development and will be added for v1.0.0

**Enforcing consistent casing**

It is way too easy to losing consistency with you casing over time. In addition to testing your responses and request bodies, the package performs case checking on every key it touches. Currently supported cases include:

- camelCase
- snake_case
- PascalCase
- kebab-case

and of course, this feature can be turned off for the whole project, or you can ignore individual keys when required.


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
        'CASE': 'camel case',
        'PATH': BASE_DIR + '/openapi-schema.yml'  # not required for drf_yasg
    }

**********
Parameters
**********

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

    *This setting is only required if you wish to test a static schema - not for drf_yasg implementations.*

|

********
Examples
********

Using drf_yasg_ for dynamic schema generation, your configuration might look like this:

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg

.. code:: python

    SWAGGER_TESTER = {
        'CASE': 'snake case'
    }

and you can test your responses like this

.. code:: python

    from django_swagger_tester.response_validation.drf_yasg import validate_response

    def test_response_documentation(client):
        response = client.get(endpoint)
        validate_response(response=response, method='GET', endpoint_url=endpoint, ignore_case=[])

While using, e.g., DRF_ for static schema generation, you would need to add the path to your generated schema:

.. _DRF: https://www.django-rest-framework.org/api-guide/schemas/

.. code:: python

    SWAGGER_TESTER = {
        'CASE': 'camel case'
        'PATH': './swagger/schema.json'
    }

and you can test your responses like this

.. code:: python

    from django_swagger_tester.response_validation.static_schema import validate_response

    def test_response_documentation(client):
        response = client.get(endpoint)
        validate_response(response=response, method='GET', endpoint_url=endpoint, ignore_case=[])


**************
Implementation
**************

It is recommended that you implement Django Swagger Tester with existing API tests. The easiest possible way to get started would be to test valid responses from an existing endpoint test. You can also test 400 and 500 errors by passing a 400 or 500 series response.

A working Django test example might look like this:

.. code:: python

    from django.contrib.auth.models import User
    from rest_framework.test import APITestCase

    from django_swagger_tester.response_validation.drf_yasg import validate_response


    class TestMyAPI(APITestCase):

        def setUp(self):
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)
            self.path = '/api/v1/cars/correct/'

        def test_get_200(self):
            """
            Verifies that a 200 is returned for a valid GET request to the /correct/ endpoint.
            """
            response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
            expected_response = [...]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # Test Swagger documentation
            validate_response(response=response, method='GET', endpoint_url=self.path)

See the demo projects and tests folder for more examples.
