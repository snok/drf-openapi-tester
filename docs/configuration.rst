.. _configuration:

*************
Configuration
*************

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
        'CASE_PASSLIST': [],
        'CAMEL_CASE_PARSER': False,
    }

.. Note::

    The ``PATH`` setting is only required if you are using the StaticSchemaLoader loader class.



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

*CASE_PASSLIST*
~~~~~~~~~~~~~~~~

List of string for ignoring exceptions from general case-testing. Say you've decided that all your responses should be camel cased, but you've already made ``IP`` a capitalized response key; you can the add the key to your ``CASE_PASSLIST`` to avoid this being flagged as an error in your tests.

Example:

.. code:: python

    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        'CASE_PASSLIST': ['IP', 'DHCP'],
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
