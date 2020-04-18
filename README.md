<p align="center">
  <a><img width="750px" src="docs/img/readme_logo4.png" alt='logo'></a>
</p>

<p align="center">
<a href="https://pypi.org/project/django-swagger-tester/">
    <img src="https://img.shields.io/pypi/v/django-swagger-tester.svg" alt="Package version">
</a>
<a href="https://pypi.org/project/django-swagger-tester/">
    <img src="https://img.shields.io/pypi/pyversions/django-swagger-tester.svg" alt="Supported Python versions">
</a>
<a href="https://pypi.python.org/pypi/django-swagger-tester">
    <img src="https://img.shields.io/pypi/djversions/django-swagger-tester.svg" alt="Supported Django versions">
</a>
<a href="https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest">
    <img src="https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest" alt="Documentation status">
</a>
<a href="https://codecov.io/gh/sondrelg/django-swagger-tester">
    <img src="https://codecov.io/gh/sondrelg/django-swagger-tester/branch/master/graph/badge.svg" alt="Code coverage">
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

---

**Documentation**: [https://django-swagger-tester.readthedocs.io/](https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest)

**Repository**: [https://github.com/sondrelg/django-swagger-tester](https://github.com/sondrelg/django-swagger-tester)

---

# Django Swagger Tester

This package is a utility for testing Django Swagger documentation, with the goal of making it easy for developers to spot documentation errors.

The package has three main features:

- [Testing response documentation](https://django-swagger-tester.readthedocs.io/en/latest/testing_with_django_swagger_tester.html#response-validation)

- [Testing input documentation](https://django-swagger-tester.readthedocs.io/en/latest/testing_with_django_swagger_tester.html#input-validation)

- [Ensuring all documentation complies with a single parameter naming standard](https://django-swagger-tester.readthedocs.io/en/latest/testing_with_django_swagger_tester.html#case-checking). Supported naming standards include `camelCase`, `snake_case`, `kebab-case`, and `PascalCase`.

Django Swagger Tester is currently compatible with Swagger documentation generated
using [drf_yasg](https://github.com/axnsan12/drf-yasg), or docs rendered from a schema file (yaml/json).
If you're using another method to generate your documentation and would like to use this library, feel free to add an issue, or create a PR.

## Installation

Install using pip:

```python
pip install django-swagger-tester
```
