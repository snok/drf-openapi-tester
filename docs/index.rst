.. raw:: html

    <p align="center"><h2 align='center'>Django OpenAPI Tester</h2></p>
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

Contents
--------

.. toctree::
    :maxdepth: 3

    supported_implementations
    installation
    configuration
    implementation
    i18n
    troubleshooting
    contributing
    publish
    changelog

.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing request body documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _Ensuring your docs comply with a single parameter naming standard (case type): https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
