.. raw:: html

    <p align="center">
        <h2 align='center'>🛠 Django Swagger Tester 🛠</h2>
    </p>
    <p align="center">
      <em>A Django test utility for validating Swagger documentation</em>
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
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Supported Python versions">
    </a>
    <a href="https://pypi.python.org/pypi/django-swagger-tester">
        <img src="https://img.shields.io/badge/django%20versions-2.2%2B-blue" alt="Supported Django versions">
    </a>
    </p>
    <p align="center">
    <a href="https://pypi.org/project/django-swagger-tester/">
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

**Documentation**: `https://django-swagger-tester.readthedocs.io <https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest>`_

**Repository**: `https://github.com/snok/django-swagger-tester <https://github.com/snok/django-swagger-tester>`_

--------------

Django Swagger Tester
=====================

Django Swagger Tester is a simple test utility for validating your Django Swagger documentation.

Its aim is to make it easy for developers to catch and correct documentation errors in their Swagger/OpenAPI docs.

Features
--------

The package has two primary features:

-  `Testing response documentation`_
-  `Testing request body documentation`_

Support for other use cases could be added in the future, and contributions are welcome.

Implementations
---------------

This package currently supports:

- Testing of dynamically rendered OpenAPI schemas using `drf-yasg`_
- Testing of dynamically rendered OpenAPI schemas using `drf-spectacular`_
- Testing any implementation which generates a static yaml or json file (e.g., like `DRF`_)


If you're using another method to generate your documentation and would like to use this package, feel free to add an issue, or create a PR. Adding a new implementation is as easy as adding the required logic needed to load the OpenAPI schema.

Contents
--------

.. toctree::
    :maxdepth: 3

    installation
    configuration
    implementation
    troubleshooting
    contributing
    publish
    changelog

.. _drf-yasg: https://github.com/axnsan12/drf-yasg
.. _drf-spectacular: https://github.com/tfranzel/drf-spectacular
.. _drf: https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas
.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing request body documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _Ensuring your docs comply with a single parameter naming standard (case type): https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
