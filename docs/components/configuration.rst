*************
Configuration
*************

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

A full example of the ``OPENAPI_TESTER`` settings might look like this:

.. code:: python

    OPENAPI_TESTER = {
        'SCHEMA_LOADER': StaticSchemaLoader,
        'PATH': 'test_project/openapi-schema.yml',
        'CASE_TESTER': is_camel_case,
        'CASE_PASSLIST': ['IP', 'DHCP'],
    }


.. Note::

    The ``PATH`` setting is only required if you are using the StaticSchemaLoader loader class.

Scroll down for info on each individual setting.

Parameters
----------

SCHEMA_LOADER
~~~~~~~~~~~~~

The loader class you use is dictated by how your OpenAPI schema is generated.
If your schema is a static file, you should use the ``StaticSchemaLoader``. If not, you should select the loader class that serves your implementation.

Loader classes can be imported from ``openapi_tester.loaders`` and currently include:

- ``StaticSchemaLoader``
- ``DrfYasgSchemaLoader``
- ``DrfSpectacularSchemaLoader``

The loader class is responsible for all logic related to loading and interacting with your OpenAPI schema.

*Example*:

.. code:: python

    from openapi_tester.loaders import DrfSpectacularSchemaLoader

    OPENAPI_TESTER = {
        'SCHEMA_LOADER': DrfSpectacularSchemaLoader,
        ...
    }

PATH
~~~~

The path parameter is only required if you're using the ``StaticSchemaLoader``
loader class, and just lets the loader class know where your schema is located in your project.

*Example*:

.. code:: python

  OPENAPI_TESTER = {
      'PATH': BASE_DIR / '/openapi-schema.yml',
  }

CASE_TESTER
~~~~~~~~~~~

The case tester function lets you add case-checking as an extra dimension to
your response validation. The idea is if you've decided your APIs should be
*camelCased*, this provides a way to enforce that standard.

The callable passed for this input decides the naming standard you wish to enforce for your documentation.

There are currently four supported options:

-  ``camel case``
-  ``snake case``
-  ``pascal case``
-  ``kebab case``
- or you can pass nothing to skip this feature

*Example*:

.. code:: python

    from openapi_tester.case_testers import is_camel_case

    OPENAPI_TESTER = {
        ...
        'CASE_TESTER': is_camel_case,
    }

**Default**: ``None``

CASE_PASSLIST
~~~~~~~~~~~~~

This setting is only useful if you've set a case tester.

The case passlist can hold a list of strings which you do *not* wish to check
for case-inconsistencies. Say you've decided that all your responses should be
camel cased, but you've already made ``IP`` a capitalized response key and don't
want to change it, you can the add the key to your ``CASE_PASSLIST`` to avoid
this being flagged as an error in your tests.

*Example*:

.. code:: python

    from openapi_tester.case_testers import is_camel_case

    OPENAPI_TESTER = {
        ...
        'CASE_PASSLIST': ['IP', 'DHCP'],
    }

**Default**: ``[]``
