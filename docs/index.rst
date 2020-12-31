.. raw:: html

    <p align="center">
        <h2 align='center'>Django OpenAPI Response Tester</h2>
    </p>
    <p align="center">
      <em>A test utility for validating API responses</em>
    </p>


.. raw:: html

    <p align="center">
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/pypi/v/django-swagger-tester.svg" alt="Package version">
    </a>
    <a href="https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest" alt="Documentation status">
    </a>
    <a href="https://codecov.io/gh/snok/django-swagger-tester">
        <img src="https://codecov.io/gh/snok/django-swagger-tester/branch/master/graph/badge.svg" alt="Code coverage">
    </a>
    <a href="https://pypi.org/project/django-openapi-response-tester/">
        <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Supported Python versions">
    </a>
    <a href="https://pypi.python.org/pypi/django-openapi-response-tester">
        <img src="https://img.shields.io/badge/django%20versions-2.2%2B-blue" alt="Supported Django versions">
    </a>
    </p>
    <p align="center">
    <a href="https://pypi.org/project/django-openapi-response-tester/">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style Black">
    </a>
    <a href="http://mypy-lang.org/">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="Pre-commit enabled">
    </a>
    </p>

--------------

**Documentation**: `https://django-openapi-response-tester.readthedocs.io <https://django-openapi-response-tester.readthedocs.io/en/latest/?badge=latest>`_

**Repository**: `https://github.com/snok/django-openapi-response-tester <https://github.com/snok/django-openapi-response-tester>`_

--------------

Django OpenAPI Response Tester
==============================

This package is a simple test utility for validating your OpenAPI response documentation.

Maintaining consistent and error-free documentation can be hard,
and ensuring correctness typically becomes exponentially harder as your documentation increases.
Response documentation in particular, is a combinatorial nightmare, as every API can have multiple methods,
where each method has multiple possible responses.

This package tries to solve this problem by testing that response documentation matches
your actual API JSON responses. This way, you can actually *know* that an API's documentation reflects reality.

Supported OpenAPI Implementations
---------------------------------

How we load your OpenAPI schema will depend on what packages you're using to
host/generate your own OpenAPI schema. We currently have schema-loader classes
created for:

- Schemas rendered dynamically using `drf-yasg`_
- Schemas rendered dynamically using `drf-spectacular`_
- Any implementation which generates a static yaml or json file (e.g., like `DRF`_)

We belive this should cover most projects, but if you're using another method to
generate your documentation and would like to use this package, feel free to
add an issue, or create a PR. Adding a new implementation is as easy as adding
the required logic needed to load the OpenAPI schema.

Contents
--------

.. toctree::
    :maxdepth: 3

    installation
    configuration
    implementation
    i18n
    troubleshooting
    contributing
    publish
    changelog

.. _drf-yasg: https://github.com/axnsan12/drf-yasg
.. _drf-spectacular: https://github.com/tfranzel/drf-spectacular
.. _drf: https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas
.. _Testing response documentation: https://django-openapi-response-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing request body documentation: https://django-openapi-response-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _Ensuring your docs comply with a single parameter naming standard (case type): https://django-openapi-response-tester.readthedocs.io/en/latest/implementation.html#case-checking
