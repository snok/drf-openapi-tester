.. _configuration:

*************
Configuration
*************

Settings
--------

To use Django Swagger Settings in your project, your first need to add a ``SWAGGER_TESTER``
object to your ``settings.py``:

.. code:: python

   SWAGGER_TESTER = {
       'CASE': 'camel case',
       'PATH': BASE_DIR + '/openapi-schema.yml'  # not required for drf_yasg implementations
   }

.. Note::

    The ``PATH`` setting is only required if you are rendering Swagger docs from a static schema.



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

By settings this to True, example values constructed in the ``validate_input_serializer`` function will be snake cased before it's passed
to a serializer. See the `function docs <implementation.html#input-validation>`_ for more info.

Example:

.. code:: python

  SWAGGER_TESTER = {
      'CAMEL_CASE_PARSER': True,
  }
