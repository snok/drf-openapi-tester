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
                'VALIDATION_EXEMPT_URLS': ['^api/v1/special-endpoint$'],
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

*Example*:

.. code:: python

    from django_swagger_tester.loaders import DrfSpectacularSchemaLoader

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': DrfSpectacularSchemaLoader,
        ...
    }

PATH
~~~~

Path takes the file path of your OpenAPI schema file. this is only required if you're using the ``StaticSchemaLoader`` loader class.

*Example*:

.. code:: python

  SWAGGER_TESTER = {
      'PATH': BASE_DIR / '/openapi-schema.yml',
  }

CASE_TESTER
~~~~~~~~~~~

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

List of string for ignoring exceptions from general case-testing. Say you've decided that all your responses should be camel cased, but you've already made ``IP`` a capitalized response key; you can the add the key to your ``CASE_PASSLIST`` to avoid this being flagged as an error in your tests.

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
``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer`` for your API views.

*Example*:

.. code:: python

  SWAGGER_TESTER = {
      'CAMEL_CASE_PARSER': True,
  }

**Default**: ``False``

MIDDLEWARE
~~~~~~~~~~

Middleware holds settings for specific middleware included in the package. There's currently only one middleware: ``ResponseValidationMiddleware``.

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

When debug is ``True`` the middleware will validate responses. The setting exists to let you deactivate tests during ci/cd, during tests, or in any environment where you don't wish for responses to be validated.

**Default**: ``True``

**VALIDATION_EXEMPT_URLS**

Takes a list of regex patterns for endpoint paths to ignore. If you have an undocumented endpoint, or any other valid use-case where you don't wish to validate responses from the endpoint, this can be useful.

**Default**: ``[]``

---------

*Example*:

.. code:: python

    SWAGGER_TESTER = {
        'MIDDLEWARE': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'DEBUG': True,
                'VALIDATION_EXEMPT_URLS': ['^api/v1/special-endpoint$'],
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
