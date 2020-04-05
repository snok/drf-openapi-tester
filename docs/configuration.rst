.. _configuration:

*************
Configuration
*************

Settings
--------

Add a ``SWAGGER_TESTER`` dict to your ``settings.py``:

.. code-block:: python

    SWAGGER_TESTER = {
        'CASE': 'camel case',
        'PATH': BASE_DIR + '/openapi-schema.yml'  # not required for drf_yasg
    }


Parameters
----------

* CASE
    The case standard you wish to enforce for your documentation.

    Needs to be one of the following:

        * :code:`camel case`
        * :code:`snake case`
        * :code:`pascal case`
        * :code:`kebab case`
        * :code:`None`

    All documentation is tested to make sure values are correctly cased, unless you specify :code:`None` to skip this feature.

    Example:

    .. code-block:: python

        SWAGGER_TESTER = {
            'CASE': 'snake case',
        }

    Default: :code:`camel case`

* PATH
    The path to your OpenAPI specification.

    Example:

    .. code-block:: python

        SWAGGER_TESTER = {
            'PATH': BASE_DIR + '/openapi-schema.yml',
        }


    *This setting is not required if your swagger docs are generated.
