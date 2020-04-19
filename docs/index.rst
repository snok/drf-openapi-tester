.. raw:: html

    <p align="center">
        <a href="https://django-swagger-tester.readthedocs.io/">
        <img width="750px" src="https://raw.githubusercontent.com/sondrelg/django-swagger-tester/master/docs/img/package_logo.png" alt='logo'></a>
    </p>
    <p align="center">
      <em>A Django test utility for validating Swagger documentation</em>
    </p>

|

.. raw:: html

    <p align="center">
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/pypi/v/django-swagger-tester.svg" alt="Package version">
    </a>
    <a href="https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest" alt="Documentation status">
    </a>
    <a href="https://codecov.io/gh/sondrelg/django-swagger-tester">
        <img src="https://codecov.io/gh/sondrelg/django-swagger-tester/branch/master/graph/badge.svg" alt="Code coverage">
    </a>
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/pypi/pyversions/django-swagger-tester.svg" alt="Supported Python versions">
    </a>
    <a href="https://pypi.python.org/pypi/django-swagger-tester">
        <img src="https://img.shields.io/pypi/djversions/django-swagger-tester.svg" alt="Supported Django versions">
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

**Repository**: `https://github.com/sondrelg/django-swagger-tester <https://github.com/sondrelg/django-swagger-tester>`_

--------------

Django Swagger Tester
=====================

This package is a simple test utility for your Django Swagger documentation.

Its aim is to make it easy for developers to catch and correct documentation errors in their Swagger docs by
comparing documented responses to actual API responses, or validating documented request bodies using actual input serializers.

Features
--------

The package has three main features:

-  `Testing response documentation`_

-  `Testing input documentation`_

-  `Ensuring your docs comply with a single parameter naming standard`_.

   Supported naming standards include ``camelCase``, ``snake_case``,
   ``kebab-case``, and ``PascalCase``.


Implementations
---------------

We currently support testing of:

- Dynamically rendered Swagger docs, using `drf_yasg`_
- All implementations which render Swagger docs from a schema file (yaml or json)

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

.. _drf_yasg: https://github.com/axnsan12/drf-yasg
.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing input documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _Ensuring your docs comply with a single parameter naming standard: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
