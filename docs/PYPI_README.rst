Django OpenAPI Tester
=====================

.. role:: python(code)
   :language: python

.. image:: https://img.shields.io/pypi/v/django-openapi-tester.svg
    :target: https://pypi.org/project/django-openapi-tester/

.. image:: https://img.shields.io/pypi/pyversions/django-openapi-tester.svg
    :target: https://pypi.org/project/django-openapi-tester/

.. image:: https://img.shields.io/pypi/djversions/django-openapi-tester.svg
    :target: https://pypi.python.org/pypi/django-openapi-tester

.. image:: https://readthedocs.org/projects/django-openapi-tester/badge/?version=latest
    :target: https://django-openapi-tester.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/snok/django-openapi-tester/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/snok/django-openapi-tester

|

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://pypi.org/project/django-openapi-tester/

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/
    :alt: Checked with mypy

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

--------------

**Documentation**: `https://django-openapi-tester.readthedocs.io <https://django-openapi-tester.readthedocs.io/en/latest/?badge=latest>`_

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

.. _Testing response documentation: https://django-openapi-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing request body documentation: https://django-openapi-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _Ensuring your docs comply with a single parameter naming standard (case type): https://django-openapi-tester.readthedocs.io/en/latest/implementation.html#case-checking
