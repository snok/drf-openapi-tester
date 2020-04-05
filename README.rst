#####################
Django Swagger Tester
#####################

.. image:: https://img.shields.io/pypi/v/django-swagger-tester.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/pypi/pyversions/django-swagger-tester.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/pypi/djversions/django-swagger-tester.svg
    :target: https://pypi.python.org/pypi/django-swagger-tester

.. image:: https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest
    :target: https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/sondrelg/django-swagger-tester/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/sondrelg/django-swagger-tester

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

This package lets you test the integrity of your OpenAPI/Swagger documentation.

The package has three main features:

* `Testing response documentation <testing_with_django_swagger_tester.html>`_
* `Testing input documentation <testing_with_django_swagger_tester.html>`_
* `Ensuring all documentation complies with a case standard <configuration.html>`_. Available standards include:

    * camelCase
    * snake_case
    * kebab-case
    * PascalCase


Django Swagger Tester is currently compatible with Swagger documentation generated using drf_yasg_, or docs rendered from a schema file (yaml/json). If you're using another method to generate your documentation and would like to use this library, feel free to add an issue, or create a PR - expanding the package is relatively simple.

************
Installation
************

Install using pip:

.. code:: bash

    pip install django-swagger-tester

*************
Configuration
*************

Settings
========

To add Django Swagger Settings in your project, add a ``SWAGGER_TESTER`` object to your ``settings.py``:

.. code-block:: python

    SWAGGER_TESTER = {
        'CASE': 'camel case',
        'PATH': BASE_DIR + '/openapi-schema.yml'  # not required for drf_yasg
    }


Setting parameters
==================

* CASE
    The case standard you wish to enforce for your documentation.

    Needs to be one of the following:

        * :code:`camel case`
        * :code:`snake case`
        * :code:`pascal case`
        * :code:`kebab case`
        * :code:`None`

    All documentation is tested to make sure values are correctly cased, unless you specify :code:`None` to skip this feature.

    Example:

    .. code-block:: python

        SWAGGER_TESTER = {
            'CASE': 'snake case',
        }

    Default: :code:`camel case`

* PATH
    The path to your OpenAPI specification.

    Example:

    .. code-block:: python

        SWAGGER_TESTER = {
            'PATH': BASE_DIR + '/openapi-schema.yml',
        }


    *This setting is not required if your swagger docs are generated.*

**********************************
Testing with django Swagger Tester
**********************************

This document contains an in-depth explanation on how the package works, and how to best implement it.

Response validation
===================

An OpenAPI schema should generally span all APIs you provide. For each API, there may be several methods to document (GET, PUT, POST, DELETE, ...), and for each method you may have several responses (200, 400, 401, 404, 5XX). Seeing that at least parts of the OpenAPI schema used for rendering your swagger docs will need to be maintained manually, it is easy to see how bugs might be introduced in the documentation over time. By testing your response documentation against your actual API responses, you can make sure that errors don't pass silently.

This functionality is currently compatible with rendered static schema, or generated `drf_yasg`_ swagger docs.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg

At the core, the logic for testing an OpenAPI schema is the same, regardless of your Swagger implementation. However, because packages like drf_yasg_ lets you generate documentation on the fly, we need custom logic for extracting the schema. The result is that we need separate implementations for separate documentation implementations, simply for loading schemas.

The validate_response function
------------------------------

The ``validate_response`` function takes three required inputs:

* response
    description: This should be the response object returned from an API call. Note: Make sure to pass the response object, not the response data, as we need to match both ``status_code`` and ``json`` to the OpenAPI schema.
    type: Response

* method
    description: This should be the HTTP method used to get the reponse.
    type: string
    example: 'GET'

* endpoint_url
    description: This should be the resolvable path of your endpoint.
    type: string
    example: 'api/v1/test'

In addition, the function also takes one optional input:

* ignore_case
    description: List of keys for which we will skip case-validation. This can be useful for when you've made a conscious decision to, e.g., keep an acronym upper-cased although you have camelCase as a general standard.
    type: list of strings
    example: ['API',]

Dynamically rendered OpenAPI schema with drf_yasg
-------------------------------------------------

The drf_yasg_ implementation can be imported from its own project folder:

.. code-block:: python

    from django_swagger_tester.response_validation.drf_yasg import validate_response


Statically rendered OpenAPI schema
----------------------------------

When testing a static schema (located locally in your project), make sure to point to the right file in the ``PATH`` setting.

The static schema implementation can be imported from its own project folder:

.. code-block:: python

    from django_swagger_tester.response_validation.static_schema import validate_response


Examples
--------

A pytest implementation might look like this:

.. code:: python

    def test_response_documentation(client):
        response = client.get('api/v1/test/')

        assert response.status_code == 200
        assert response.json() == expected_response

        # Test Swagger documentation
        validate_response(response=response, method='GET', endpoint_url='api/v1/test/', ignore_case=[])

A Django-test implementation might look like this:

.. code-block:: python

    class MyApiTest(APITestCase):

        def setUp(self) -> None:
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)
            self.path = '/api/v1/test/'

        def test_get_200(self) -> None:
            """
            Verifies that a 200 is returned for a valid GET request to the /test/ endpoint.
            """
            response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
            expected_response = [...]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # Test Swagger documentation
            validate_response(response=response, method='GET', endpoint_url=self.path)

You can also test more than a single response at the time.

.. code:: python

    def test_response_documentation(client):
        # 201 - Resource created
        response = client.post('api/v1/test/', data=...)
        validate_response(response=response, method='POST', endpoint_url='api/v1/test/', ignore_case=[])

        # 200 - Idempotency --> if an object exists, return it with a 200 without creating a new resource
        response = client.post('api/v1/test/', data=...)
        validate_response(response=response, method='POST', endpoint_url='api/v1/test/', ignore_case=[])

        # 400 - Bad data
        response = client.post('api/v1/test/', data=bad_data)
        validate_response(response=response, method='POST', endpoint_url='api/v1/test/', ignore_case=[])

Input validation
================

Similarly to the response documentation, request body examples should be representative of a functioning request body. If you use Django Rest Framework's `Serializer` class for input validation, it is simple to make sure that all your documented request bodies would pass input validation for all endpoints.

This is currently under development and will be added for v1.0.0
