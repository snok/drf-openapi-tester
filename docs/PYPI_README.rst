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

-  `Ensuring your docs comply with a single parameter naming standard`_.

   Supported naming standards include ``camelCase``, ``snake_case``,
   ``kebab-case``, and ``PascalCase``.


Implementations
---------------

We currently support testing of:

- Dynamically rendered Swagger docs, using `drf_yasg`_
- All implementations which render Swagger docs from a schema file (yaml or json)

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

To use Django Swagger Settings in your project, your first need to add a ``SWAGGER_TESTER``
object to your ``settings.py``:

.. code:: python

   SWAGGER_TESTER = {
       'CASE': 'camel case',
       'PATH': BASE_DIR + '/openapi-schema.yml'  # not required for drf_yasg implementations
   }

Parameters
----------

*CASE*
~~~~~~

The parameter naming standard you wish to enforce for your documentation.

Needs to be one of the following:

-  ``camel case``
-  ``snake case``
-  ``pascal case``
-  ``kebab case``
-  ``None``

Your OpenAPI schema will be assessed to make sure all parameter names
are correctly cased according to this preference. If you do not wish
to enforce this check, you can specify ``None`` to skip this feature.

Example:

.. code:: python

  SWAGGER_TESTER = {
      'CASE': 'snake case',
  }

**Default**: ``camel case``

*PATH*
~~~~~~

The path to your OpenAPI specification.

Example:

.. code:: python

  SWAGGER_TESTER = {
      'PATH': BASE_DIR + '/openapi-schema.yml',
  }

*This setting is not required if your swagger docs are generated.*

*CAMEL_CASE_PARSER*
~~~~~~~~~~~~~~~~~~~

Should be set to ``True`` if you use `djangorestframework-camel-case <https://github.com/vbabiy/djangorestframework-camel-case>`_'s
``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer`` for your API views.

By settings this to True, example values constructed in the ``validate_input`` function will be snake cased before it's passed
to a serializer. See the `function docs <https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#the-validate-input-function>`_ for more info.

Example:

.. code:: python

  SWAGGER_TESTER = {
      'CAMEL_CASE_PARSER': True,
  }


Response Validation
===================

To verify that your API response documentation is correct, we test the
generated documentation against actual API responses.

A pytest implementation might look like this:

.. code:: python

   from django_swagger_tester.drf_yasg import validate_response  # or replace drf_yasg with `static_schema`


   def test_response_documentation(client):
       response = client.get('api/v1/test/')

       assert response.status_code == 200
       assert response.json() == expected_response

       # Test Swagger documentation
       validate_response(response=response, method='GET', route='api/v1/test/')

A Django-test implementation might look like this:

.. code:: python

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
           validate_response(response=response, method='GET', route=self.path)

You can also test more than a single response at the time:

.. code:: python

    def test_response_documentation(client):
        # 201 - Resource created
        response = client.post('api/v1/test/', data=...)
        validate_response(response=response, method='POST', route='api/v1/test/')

        # 200 - Idempotency --> if an object exists, return it with a 200 without creating a new resource
        response = client.post('api/v1/test/', data=...)
        validate_response(response=response, method='POST', route='api/v1/test/')

        # 400 - Bad data
        response = client.post('api/v1/test/', data=bad_data)
        validate_response(response=response, method='POST', route='api/v1/test/')

Input Validation
================

To make sure your request body documentation is accurate, and will stay accurate, it can be useful to set up tests.

Considering most APIs will use input serializers for input validation, it seems sensible to just run the
example documentation on your serializer.

A pytest implementation of input validation might look like this::

    from myapp.api.serializers import MyAPISerializer  # <-- your custom serializer


    def test_request_body_documentation(client):
        """
        Verifies that our request body documentation is representative of a valid request body.
        """
        from django_swagger_tester.drf_yasg import validate_input  # or replace drf_yasg with `static_schema`
        validate_input(serializer=MyAPISerializer, method='POST', route='api/v1/test/', camel_case_parser=True)


The ``camel_case_parser`` argument should be set to ``True`` if you are using ``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer``
from the `djangorestframework-camel-case <https://github.com/vbabiy/djangorestframework-camel-case>`_ package.

.. _`https://django-swagger-tester.readthedocs.io/`: https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest
.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing input documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _Ensuring your docs comply with a single parameter naming standard: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
.. _drf_yasg: https://github.com/axnsan12/drf-yasg
.. _documentation: https://django-swagger-tester.readthedocs.io/
.. _docs: https://django-swagger-tester.readthedocs.io/
