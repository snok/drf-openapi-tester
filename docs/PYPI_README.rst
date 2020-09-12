Django Swagger Tester
=====================

.. role:: python(code)
   :language: python

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

|

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/
    :alt: Checked with mypy

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

--------------

**Documentation**: `https://django-swagger-tester.readthedocs.io <https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest>`_

**Repository**: `https://github.com/sondrelg/django-swagger-tester <https://github.com/sondrelg/django-swagger-tester>`_

--------------



This package is a simple test utility for your Django Swagger documentation.

Its aim is to make it easy for developers to catch and correct documentation errors in their Swagger docs by
comparing documented responses to actual API responses, or validating documented request bodies using actual input serializers.

Features
--------

The package has three main features:

-  `Testing response documentation`_

-  `Testing input documentation`_

-  and `ensuring your docs comply with a single parameter naming standard (case type)`_.

   Supported naming standards include ``camelCase``, ``snake_case``,
   ``kebab-case``, and ``PascalCase``.


Implementations
---------------

This package currently supports:

- Testing of dynamically rendered OpenAPI schemas using using `drf_yasg`_
- Testing of any implementation which generates a static schema yaml or json file (e.g., like `DRF`_)


If you're using another method to generate your documentation and would like to use this package, feel free to add an issue, or create a PR. Adding a new implementation is as easy as adding the required logic needed to load the OpenAPI schema.

Installation
============

Install using pip:

.. code:: python

   pip install django-swagger-tester

Configuration
=============

Settings
--------

To use Django Swagger Settings in your project, you first need to add a ``django_swagger_tester`` to your installed apps.

.. code:: python

    INSTALLED_APPS = [
        ...
        'django_swagger_tester',
    ]

Secondly, you need to configure the ``SWAGGER_TESTER`` package settings in your ``settings.py``:

.. code:: python

    from django_swagger_tester.loaders import StaticSchemaLoader
    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': StaticSchemaLoader,
        'PATH': './static/openapi-schema.yml',
        'CASE_TESTER': is_camel_case,
        'CASE_WHITELIST': [],
        'CAMEL_CASE_PARSER': False,
    }

Parameters
----------

*SCHEMA_LOADER*
~~~~~~~~~~~~~~~

The loader class you use is dictated by how your OpenAPI schema is generated. If your schema is a static file, you should use the ``StaticSchemaLoader``. If not, you should select the loader class that serves your implementation.

Loader classes can be imported from ``django_swagger_tester.loaders`` and currently include:

- ``StaticSchemaLoader``
- ``DrfYasgSchemaLoader``

Example:

.. code:: python

    from django_swagger_tester.loaders import DrfYasgSchemaLoader

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': DrfYasgSchemaLoader,
    }


*PATH*
~~~~~~

Path takes the file path of your OpenAPI schema file. this is only required if you're using the ``StaticSchemaLoader`` loader class.

Example:

.. code:: python

  SWAGGER_TESTER = {
      'PATH': BASE_DIR / '/openapi-schema.yml',
  }

*CASE_TESTER*
~~~~~~~~~~~~~

The callable passed for this input decide the naming standard you wish to enforce for your documentation.

There are currently four supported options:

-  ``camel case``
-  ``snake case``
-  ``pascal case``
-  ``kebab case``
- or you can pass ``None`` to skip case validation completely

Your OpenAPI schema will be tested to make sure all parameter names
are correctly cased according to this preference. If you do not wish
to enforce this check, you can specify ``None`` to skip this feature.

Example:

.. code:: python

    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        'CASE_TESTER': is_camel_case,
    }

**Default**: ``None``

*CASE_WHITELIST*
~~~~~~~~~~~~~~~~

List of string for ignoring exceptions from general case-testing. Say you've decided that all your responses should be camel cased, but you've already made ``IP`` a capitalized response key; you can the add the key to your ``CASE_WHITELIST`` to avoid this being flagged as an error in your tests.

Example:

.. code:: python

    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        'CASE_WHITELIST': ['IP', 'DHCP'],
    }

**Default**: ``[]``

*CAMEL_CASE_PARSER*
~~~~~~~~~~~~~~~~~~~

Should be set to ``True`` if you use `djangorestframework-camel-case <https://github.com/vbabiy/djangorestframework-camel-case>`_'s
``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer`` for your API views.

Example:

.. code:: python

  SWAGGER_TESTER = {
      'CAMEL_CASE_PARSER': True,
  }

**Default**: ``False``


Response Validation
===================

To make sure your API response matches your documented response, the ``validate_response`` function compares the two at each level of depth.

A pytest implementation might look like this:

.. code:: python

    from django_swagger_tester.testing import validate_response

    def test_200_response_documentation(client):
        route = 'api/v1/test/1'
        response = client.get(route)
        assert response.status_code == 200
        assert response.json() == expected_response

        # test swagger documentation
        validate_response(response=response, method='GET', route=route)

A Django-test implementation might look like this:

.. code-block:: python

    from django_swagger_tester.testing import validate_response

    class MyApiTest(APITestCase):

        path = '/api/v1/test/'

        def setUp(self) -> None:
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)

        def test_get_200(self) -> None:
            response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
            expected_response = [...]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # test swagger documentation
            validate_response(response=response, method='GET', route=self.path)

It is also possible to test more than a single response at the time:

.. code:: python

    def test_post_endpoint_responses(client):
        # 201 - Resource created
        response = client.post(...)
        validate_response(response=response, method='POST', route='api/v1/test/')

        # 400 - Bad data
        response = client.post(...)
        validate_response(response=response, method='POST', route='api/v1/test/')

    def test_get_endpoint_responses(client):
        # 200 - Fetch resource
        response = client.get(...)
        validate_response(response=response, method='GET', route='api/v1/test/<id>')

        # 404 - Bad ID
        response = client.get(...)
        validate_response(response=response, method='GET', route='api/v1/test/<bad id>')

Input Validation
================

To make sure your request body documentation is accurate, and will stay accurate, you can use endpoint serializers to validate your schema directly.

``validate_input_serializer`` constructs an example representation of the documented request body, and passes it to the serializer it is given. This means it's only useful if you use serializers for validating your incoming request data.

A Django test implementation of input validation for a whole project could be structured like this:

.. code:: python

    from django.test import SimpleTestCase
    from django_swagger_tester.testing import validate_input_serializer

    from api.serializers.validation.request_bodies import ...


    class TestSwaggerInput(SimpleTestCase):
        endpoints = [
            {
                'api/v1/orders/': [
                    ('POST', ValidatePostOrderBody),
                    ('PUT', ValidatePutOrderBody),
                    ('DELETE', ValidateDeleteOrderBody)
                ]
            },
            {
                'api/v1/orders/<id>/entries/': [
                    ('POST', ValidatePostEntryBody),
                    ('PUT', ValidatePutEntryBody),
                    ('DELETE', ValidateEntryDeleteBody)
                ]
            },
        ]

        def test_swagger_input(self) -> None:
            """
            Verifies that the documented request bodies are valid.
            """
            for endpoint in self.endpoints:
                for route, values in endpoint.items():
                    for method, serializer in values:
                        validate_input_serializer(serializer=serializer, method=method, route=route)

.. _`https://django-swagger-tester.readthedocs.io/`: https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest
.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing input documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _ensuring your docs comply with a single parameter naming standard (case type): https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
.. _drf_yasg: https://github.com/axnsan12/drf-yasg
.. _documentation: https://django-swagger-tester.readthedocs.io/
.. _docs: https://django-swagger-tester.readthedocs.io/
.. _drf: https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas
