.. _configuration:

*************
Configuration
*************

Settings
--------

To use Django Swagger Settings in your project, you first need to add ``django_swagger_tester`` to your installed apps.

.. code:: python

    INSTALLED_APPS = [
        ...
        'django_swagger_tester',
    ]

Second, you need to configure the ``SWAGGER_TESTER`` package settings in your ``settings.py``. At minimum you need to specify which schema loader class to use to load your OpenAPI schema when testing it:

.. code:: python

    from django_swagger_tester.loaders import StaticSchemaLoader
    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': DrfSpectacularSchemaLoader,
    }

A complete example of the ``SWAGGER_TESTER`` settings might look like this:

.. code:: python

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': StaticSchemaLoader,
        'PATH': 'demo/openapi-schema.yml',
        'CASE_TESTER': is_camel_case,
        'CAMEL_CASE_PARSER': True,
        'CASE_PASSLIST': ['IP', 'DHCP'],
        'MIDDLEWARE': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'LOGGER_NAME': 'response_validation_middleware',
                'DEBUG': True,
                'VALIDATION_EXEMPT_URLS': [
                    {'url': '^api/v1/special-endpoint$', 'status_codes': ['*']},
                    {'url': '^api/v1/another-special-endpoint$', 'status_codes': [204]},
                ],
                'VALIDATION_EXEMPT_STATUS_CODES': [401],
            }
        },
        'VIEWS': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'LOGGER_NAME': 'django_swagger_tester',
                'DEBUG': True,
            }
        },
    }

.. Note::

    The ``PATH`` setting is only required if you are using the StaticSchemaLoader loader class.



Parameters
----------

SCHEMA_LOADER
~~~~~~~~~~~~~

The loader class you use is dictated by how your OpenAPI schema is generated. If your schema is a static file, you should use the ``StaticSchemaLoader``. If not, you should select the loader class that serves your implementation.

Loader classes can be imported from ``django_swagger_tester.loaders`` and currently include:

- ``StaticSchemaLoader``
- ``DrfYasgSchemaLoader``
- ``DrfSpectacularSchemaLoader``

The loader class is responsible for all logic related to loading and interacting with your OpenAPI schema.

*Example*:

.. code:: python

    from django_swagger_tester.loaders import DrfSpectacularSchemaLoader

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': DrfSpectacularSchemaLoader,
        ...
    }

PATH
~~~~

The path parameter is only required if you're using the ``StaticSchemaLoader`` loader class, and just lets the loader class know where your schema is located in your project.

*Example*:

.. code:: python

  SWAGGER_TESTER = {
      'PATH': BASE_DIR / '/openapi-schema.yml',
  }

CASE_TESTER
~~~~~~~~~~~

The case tester function lets you add case-checking as an extra dimension to your response validation. The idea is that
most APIs should have a standard.

The callable passed for this input decides the naming standard you wish to enforce for your documentation.

There are currently four supported options:

-  ``camel case``
-  ``snake case``
-  ``pascal case``
-  ``kebab case``
- or you can not pass anything to skip this feature

*Example*:

.. code:: python

    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        ...
        'CASE_TESTER': is_camel_case,
    }

**Default**: ``None``

CASE_PASSLIST
~~~~~~~~~~~~~

This setting is only required if you've set a case tester.

The case passlist can hold a list of strings which you do *not* wish to check for case-inconsistencies. Say you've decided that all your responses should be camel cased, but you've already made ``IP`` a capitalized response key; you can the add the key to your ``CASE_PASSLIST`` to avoid this being flagged as an error in your tests.

*Example*:

.. code:: python

    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        ...
        'CASE_PASSLIST': ['IP', 'DHCP'],
    }

**Default**: ``[]``

CAMEL_CASE_PARSER
~~~~~~~~~~~~~~~~~

Should be set to ``True`` if you use `djangorestframework-camel-case <https://github.com/vbabiy/djangorestframework-camel-case>`_'s
``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer`` for your API views. Otherwise, set it to False or leave it out of your settings.

*Example*:

.. code:: python

  SWAGGER_TESTER = {
      'CAMEL_CASE_PARSER': True,
  }

**Default**: ``False``

MIDDLEWARE
~~~~~~~~~~

Middleware holds settings for specific middlewares included in the package. There's currently only one middleware: ``ResponseValidationMiddleware``.

RESPONSE_VALIDATION
===================

These settings control how the response validation middleware behaves. Currently there are four settings to (optionally) configure.

**LOG_LEVEL**

Log level sets the level for which errors found will be logged. The idea is that, instead of raising exceptions when a response is found to not match the documented OpenAPI schema, an error message will be logged, letting you act on it without interfering with the request/response flow.

**Default**: ``ERROR``

**LOGGER_NAME**

Logger name lets you overwrite the default logger name to whatever you like.

**Default**: ``django_swagger_tester``

**DEBUG**

When debug is ``True`` the middleware will validate responses. The setting exists to let you deactivate tests during ci/cd, during tests, or in any environment where you don't wish for responses to be validated. For example, the middleware might not be of any value when you're running automated tests during CI.

**Default**: ``True``

**VALIDATION_EXEMPT_URLS**

Takes a list of dicts. The dict should contain a ``url`` key with a regex patterns for an endpoint path to ignore and a ``status_codes`` list of status codes to ignore. If you wish to ignore all status codes you can pass ``"*"`` to the list.

If you have an undocumented endpoint, an undocumented response code, or any other valid use-case where you don't wish to validate responses from the endpoint, this can be useful.

**Default**: ``[]``

**VALIDATION_EXEMPT_STATUS_CODES**

Takes a list of integer status codes for which middleware will skip validation. For instance, you may not want to document 401 responses in your schema. If that's the case, you can blanket ignore responses containing 401 status codes.

**Default**: ``[]``

---------

*Example*:

.. code:: python

    SWAGGER_TESTER = {
        'MIDDLEWARE': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'DEBUG': True,
                'VALIDATION_EXEMPT_URLS': [
                    {'url': '^api/v1/special-endpoint$', 'status_codes': ['*']},
                    {'url': '^api/v1/another-special-endpoint$', 'status_codes': [204]},
                ],
                'VALIDATION_EXEMPT_STATUS_CODES': [401, 500],
            }
        },
    }

VIEWS
~~~~~~~~~~

Views holds settings for specific view classes included in the package. There's currently only one view class: ``ResponseValidationView``.

RESPONSE_VALIDATION
===================

These settings control how the response validation middleware behaves. Currently there are three settings to (optionally) configure.

**LOG_LEVEL**

Log level sets the level for which errors found will be logged. The idea is that, instead of raising exceptions when a response is found to not match the documented OpenAPI schema, an error message will be logged, letting you act on it without interfering with the request/response flow.

**Default**: ``ERROR``

**LOGGER_NAME**

Logger name lets you overwrite the default logger name to whatever you like.

**Default**: ``django_swagger_tester``

**DEBUG**

When debug is ``True`` the view will validate responses. The setting exists to let you deactivate tests during ci/cd, during tests, or in any environment where you don't wish for responses to be validated.

**Default**: ``True``

---------

*Example*:

.. code:: python

    SWAGGER_TESTER = {
        'VIEWS': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'DEBUG': True,
            }
        },
    }

.. Note::

    The response validation view settings do not have an ``exempt status codes`` setting, but you can configure this directly in your view class.

    See the response validation view implementation section for more details.
