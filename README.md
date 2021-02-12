# DRF OpenAPI Tester

<div align="center">
    <a href="https://pypi.org/project/drf-openapi-tester/">
        <img src="https://img.shields.io/pypi/v/drf-openapi-tester.svg" alt="Package version">
    </a>
    <a href="https://codecov.io/gh/snok/drf-openapi-tester">
        <img src="https://codecov.io/gh/snok/drf-openapi-tester/branch/master/graph/badge.svg" alt="Code coverage">
    </a>
    <a href="https://pypi.org/project/drf-openapi-tester/">
        <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Supported Python versions">
    </a>
    <a href="https://pypi.python.org/pypi/drf-openapi-tester">
        <img src="https://img.shields.io/badge/django%20versions-2.2%2B-blue" alt="Supported Django versions">
    </a>
    <a href="http://mypy-lang.org/">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
    </a>
</div>

DRF OpenAPI Tester is a test utility to validate API responses against OpenApi 2/3 schema. It has built-in support for:

- Testing dynamically rendered OpenAPI 2 schemas created with [drf-yasg](https://github.com/axnsan12/drf-yasg)
- Testing dynamically rendered OpenAPI 3 schemas created
  with [drf-spectacular](https://github.com/tfranzel/drf-spectacular)
- Testing OpenAPI 2/3 yaml or json schema files (
  e.g. [DRF](https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas))

* NOTE regarding OpenAPI 2 (swagger) schemas. We are using [prance](https://github.com/jfinkhaeuser/prance) as a schema
  resolver, and it has some issues with the resolution of (very) complex OpenAPI 2.0 schemas. If you encounter
  issues, [please document them here](https://github.com/snok/drf-openapi-tester/issues/205).

## Installation

```shell script
pip install drf-openapi-tester
```

## Usage

First instantiate one or more instances of SchemaTester:

```python
from openapi_tester import SchemaTester

schema_tester = SchemaTester()


```

If you are using either [drf-yasg](https://github.com/axnsan12/drf-yasg)
or [drf-spectacular](https://github.com/tfranzel/drf-spectacular) this will be auto-detected, and the schema will be
loaded by the SchemaTester automatically. If you are using schema files though, you will need to pass the file path to
the tester:

```python
from openapi_tester import SchemaTester

schema_tester = SchemaTester(schema_file_path="./schemas/publishedSpecs.yaml")  # should be an instance of `str


```

Once you instantiates a tester, you can use it to validate a DRF Response in a test:

```python
from openapi_tester.schema_tester import SchemaTester

# you need to create at least one instance of SchemaTester.
# you can pass kwargs to it
schema_tester = SchemaTester()


def test_response_documentation(client):
    response = client.get('api/v1/test/1')

    assert response.status_code == 200

    schema_tester.validate_response(response=response)
```

If you are using the Django testing framework, you can create a base APITestCase with schema validation for easy
sharing:

```python
from openapi_tester.schema_tester import SchemaTester
from rest_framework.test import APITestCase
from rest_framework.response import Response

schema_tester = SchemaTester()


class BaseAPITestCase(APITestCase):
    """ Base test class for api views including schema validation """

    @staticmethod
    def assertResponse(
            response: Response, **kwargs
    ) -> None:
        """ helper to run validate_response and pass kwargs to it """
        schema_tester.validate_response(response=response, **kwargs)
```

Then use it in a test file:

```python
from shared.testing import BaseAPITestCase


class MyAPITests(BaseAPITestCase):
    def test_some_view(self):
        response = self.client.get("...")
        self.assertResponse(response)
```

## Options

We currently support the following optional kwargs:

### Case tester

The case tester argument takes a callable to validate the case of both your response schemas and responses. If nothing
is passed, case validation is skipped.

The library currently has 4 build-in functions that can be used:

- `is_pascal_case`
- `is_snake_case`
- `is_camel_case`
- `is_kebab-case`

for example:

```python
from openapi_tester import SchemaTester, is_camel_case

schema_test_with_case_validation = SchemaTester(case_tester=is_camel_case)

```

or

```python
from openapi_tester import SchemaTester, is_camel_case

schema_tester = SchemaTester()


def my_test():
    response = client.get('api/v1/test/1')

    assert response.status_code == 200

    schema_tester.validate_response(response=response, case_tester=is_camel_case)
```

You of course pass your own custom validator function.

### Ignore case

List of keys to ignore. In some cases you might want to declare a global list of keys exempt from case testing.

for example:

```python
from openapi_tester import SchemaTester, is_camel_case

schema_test_with_case_validation = SchemaTester(case_tester=is_camel_case, ignore_case=["IP"])

```

## Schema Validation

When the SchemaTester loads a schema, it runs it through
[OpenAPI Spec validator](https://github.com/p1c2u/openapi-spec-validator) which validates that the schema passes
without specification compliance issues. In case of issues the validator will raise an error.

## Contributing

Contributions are welcome. Please see the [contributing guide](CONTRIBUTING.md)
