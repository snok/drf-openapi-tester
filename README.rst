.. raw:: html

    <p align="center"><h1 align='center'>Django OpenAPI Tester</h1></p>
    <p align="center"><em>A test utility for validating API responses</em></p>

.. raw:: html

    <p align="center">
        <a href="https://pypi.org/project/django-swagger-tester/">
            <img src="https://img.shields.io/pypi/v/django-swagger-tester.svg" alt="Package version">
        </a>
        <a href="https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest">
            <img src="https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest" alt="Documentation status">
        </a>
        <a href="https://codecov.io/gh/snok/django-openapi-tester">
            <img src="https://codecov.io/gh/snok/django-openapi-tester/branch/master/graph/badge.svg" alt="Code coverage">
        </a>
        <a href="https://pypi.org/project/django-openapi-tester/">
            <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Supported Python versions">
        </a>
        <a href="https://pypi.python.org/pypi/django-openapi-tester">
            <img src="https://img.shields.io/badge/django%20versions-2.2%2B-blue" alt="Supported Django versions">
        </a>
        <a href="http://mypy-lang.org/">
            <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
        </a>
    </p>

--------------

**Documentation**: `https://django-swagger-tester.readthedocs.io <https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest>`_

**Repository**: `https://github.com/snok/django-openapi-tester <https://github.com/snok/django-openapi-tester>`_

--------------

Django OpenAPI Tester is a simple test utility. Its aim is to make it easy for
developers to catch and correct documentation errors in their OpenAPI schema.

.. raw::

    <img src="https://github.com/snok/django-openapi-tester/blob/docs/docs/gifs/example.gif"/>

Maintaining good documentation is hard, and ensuring complete correctness is
harder. By testing that your **actual** API responses against your schema,
you can *know* that your schema reflects reality.

To illustrate; given this example response:


.. code-block:: python

    {
      "id": 0,
      "name": "doggie",
      "status": "available"
      "photoUrls": ["string"],
      "tags": [{"id": 0, "name": "string"}],
      "category": {"id": 0, "name": "string"},
    }

your brain shouldn't have to manually scan this OpenAPI response schema for
possible documentation errors

.. code-block:: python

  "responses": {
    "200": {
      "description": "successful operation",
      "schema": {
        "type": "object",
        "required": [
          "name",
          "photoUrls"
        ],
        "properties": {
          "id": {
            "type": "integer",
            "format": "int64"
          },
          "category": {
            "type": "object",
            "properties": {
              "id": {
                "type": "integer",
                "format": "int64"
              },
              "name": {
                "type": "string"
              }
            },
            "xml": {
              "name": "Category"
            }
          },
          "name": {
            "type": "string",
            "example": "doggie"
          },
          "photoUrl": {
            "type": "array",
            "xml": {
              "wrapped": true
            },
            "items": {
              "type": "string",
              "xml": {
                "name": "photoUrl"
              }
            }
          },
          "tags": {
            "type": "array",
            "xml": {
              "wrapped": true
            },
            "items": {
              "type": "object",
              "properties": {
                "id": {
                  "type": "integer",
                  "format": "int64"
                },
                "name": {
                  "type": "string"
                }
              },
              "xml": {
                "name": "Tag"
              }
            }
          },
          "status": {
            "type": "string",
            "description": "pet status in the store",
            "enum": [
              "available",
              "pending",
              "sold"
            ]
          }
        },
        "xml": {
          "name": "Pet"
        }
      }
    }
  }

when automated tests can simply tell you that ``photoUrls`` is missing an ``s``.

Not only that, but when you come back and change your API next year, your test
suite should not allow you to deploy your changes without remembering to
update your documentation.

Implementations
---------------

This package currently supports:

- Testing of dynamically rendered OpenAPI schemas using `drf-yasg`_
- Testing of dynamically rendered OpenAPI schemas using `drf-spectacular`_
- Testing any implementation which generates a static yaml or json file (e.g., like `DRF`_)

If you're using another method to generate your documentation and would like to use this package, feel free to add an issue, or create a PR. Adding a new implementation is as easy as adding the required logic needed to load the OpenAPI schema.

Installation
============

Install using pip:

.. code:: python

   pip install django-openapi-tester

Configuration
=============

Settings
--------

To use the ``validate_response`` function in your project, you first need to
configure the ``OPENAPI_TESTER`` package settings in your ``settings.py``.
At minimum we need to know schema loader class to use to load your OpenAPI schema:

.. code:: python

    from openapi_tester.loaders import StaticSchemaLoader

    OPENAPI_TESTER = {
        'SCHEMA_LOADER': DrfSpectacularSchemaLoader,
    }

See the configuration_ section of the docs for more info.

.. _configuration: https://django-swagger-tester.readthedocs.io/en/latest/configuration.html


|
|

Response Validation
===================


**Pytest**

.. code:: python

    from openapi_tester.testing import validate_response

    def test_200_response_documentation(client):
        route = 'api/v1/test/1'
        response = client.get(route)

        assert response.status_code == 200
        assert response.json() == expected_response

        validate_response(response=response, method='GET', route=route)

**Django test**

.. code-block:: python

    from openapi_tester.testing import validate_response

    class MyApiTest(APITestCase):

        path = '/api/v1/test/'

        def setUp(self) -> None:
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)

        def test_get_200(self) -> None:
            """
            Verifies that a 200 is returned for a valid GET request to the /test/ endpoint.
            """
            response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
            expected_response = [...]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            validate_response(response=response, method='GET', route=self.path)

Error messages
~~~~~~~~~~~~~~

When found, errors will be raised in the following format:

.. code-block:: shell

    openapi_tester.exceptions.SwaggerDocumentationError: Item is misspecified:

    Summary
    -------------------------------------------------------------------------------------------

    Error:      The following properties seem to be missing from your response body: length, width.

    Expected:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}
    Received:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'}

    Hint:       Remove the key(s) from you Swagger docs, or include it in your API response.
    Sequence:   init.list

    -------------------------------------------------------------------------------------------

    * If you need more details: set `verbose=True`

- ``Expected`` describes the response data
- ``Received`` describes the schema.
- ``Hint`` will sometimes include a suggestion for what actions to take, to correct an error.
- ``Sequence`` will indicate how the response tester iterated through the data structure, before finding the error.

In this example, the response data is missing two attributes, ``height`` and ``width``, documented in the OpenAPI schema indicating that either the response needs to include more data, or that the OpenAPI schema should be corrected. It might be useful to highlight that we can't be sure whether the response or the schema is wrong; only that they are inconsistent.

.. Note::

    It can be useful to test more than just successful responses::

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


The validate_response function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``validate_response`` function takes three required inputs:

* response
    **description**: The response object returned from an API call.

    **type**: Response

    .. Note::

        Make sure to pass the response object, not the response data.

* method
    **description**: The HTTP method used to get the response.

    **type**: string

    **example**: ``method='GET'``


* route
    **description**: The resolvable path of your API.

    **type**: string

    **example**: ``route='api/v1/test'``


In addition, the function also takes two optional inputs:

* ignore_case
    **description**: List of keys for which we will skip case-validation. This can be useful for when you've made a conscious decision to, e.g., keep an acronym upper-cased although you have camelCase as a general standard.

    **type**: List of strings

    **example**: ``ignore_case=['API', 'IP]``

* verbose
    **description**: Whether to output more detailed error messages.

    **type**: bool

    **default**: ``False``

    **example**: ``verbose=True``


Suggested use
~~~~~~~~~~~~~

The response validation function can be called from anywhere,
but because the tests require a request client it generally makes sense to include
these tests with your existing API view tests.

For example::

    class TestGetCustomers(AuthorizedRequestBase):

        ...

        def test_is_valid(self):
            """
            Verify that we get a 200 from a valid request.
            """
            response = self.get(route='api/v1/customers/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

        def test_swagger_schema(self):
            """
            Verifies that the API response matches the swagger documentation for the endpoint.
            """
            response = self.get(route='api/v1/customers/')
            validate_response(response=response, method='GET', route='api/v1/customers/')

        ...

.. _`https://django-swagger-tester.readthedocs.io/`: https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest
.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing input documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _ensuring your docs comply with a single parameter naming standard (case type): https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
.. _drf_yasg: https://github.com/axnsan12/drf-yasg
.. _documentation: https://django-swagger-tester.readthedocs.io/
.. _docs: https://django-swagger-tester.readthedocs.io/
.. _drf: https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas
.. _drf-yasg: https://github.com/axnsan12/drf-yasg
.. _drf-spectacular: https://github.com/tfranzel/drf-spectacular
.. _parameter docs: https://django-swagger-tester.readthedocs.io/en/latest/configuration.html#parameters
.. _Testing request body documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
