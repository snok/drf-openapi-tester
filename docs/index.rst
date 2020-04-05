#####################
Django Swagger Tester
#####################

.. image:: https://img.shields.io/pypi/v/django-swagger-tester.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/pypi/pyversions/django-swagger-tester.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/pypi/djversions/django-swagger-tester.svg
    :target: https://pypi.python.org/pypi/django-swagger-tester

.. image:: https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest
    :target: https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/sondrelg/django-swagger-tester/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/sondrelg/django-swagger-tester

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://pypi.org/project/django-swagger-tester/

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

This package lets you test the integrity of your OpenAPI/Swagger documentation.

The package has three main features:

* `Testing response documentation <testing_with_django_swagger_tester.html>`_
* `Testing input documentation <testing_with_django_swagger_tester.html>`_
* `Ensuring all documentation complies with a case standard <configuration.html>`_. Available standards include:

    * camelCase
    * snake_case
    * kebab-case
    * PascalCase


Django Swagger Tester is currently compatible with Swagger documentation generated using drf_yasg_, or docs rendered from a schema file (yaml/json). If you're using another method to generate your documentation and would like to use this library, feel free to add an issue, or create a PR - expanding the package is relatively simple.

Contents
--------

.. toctree::
    :maxdepth: 3

    installation
    configuration
    testing_with_django_swagger_tester
    troubleshooting
    contributing
    publish
    changelog

.. _drf_yasg: https://github.com/axnsan12/drf-yasg
