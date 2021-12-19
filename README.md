[![PyPI](https://img.shields.io/pypi/v/drf-openapi-tester.svg)](https://pypi.org/project/drf-openapi-tester/)
[![Coverage](https://codecov.io/gh/snok/drf-openapi-tester/branch/master/graph/badge.svg)](https://codecov.io/gh/snok/drf-openapi-tester)
[![Python versions](https://img.shields.io/badge/Python-3.7%2B-blue)](https://pypi.org/project/drf-openapi-tester/)
[![Django versions](https://img.shields.io/badge/Django-3.0%2B-blue)](https://pypi.org/project/drf-openapi-tester/)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)

# DRF OpenAPI Tester

This is a test utility to validate DRF Test Responses against OpenAPI 2 and 3 schema. It has built-in support for:

- OpenAPI 2/3 yaml or json schema files.
- OpenAPI 2 schemas created with [drf-yasg](https://github.com/axnsan12/drf-yasg).
- OpenAPI 3 schemas created with [drf-spectacular](https://github.com/tfranzel/drf-spectacular).

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

# path should be a string
schema_tester = SchemaTester(schema_file_path="./schemas/publishedSpecs.yaml")


```

Once you instantiate a tester, you can use it to test responses:

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

If you are using the Django testing framework, you can create a base APITestCase that incorporates schema validation:

```python
from openapi_tester.schema_tester import SchemaTester
from rest_framework.test import APITestCase
from rest_framework.response import Response

schema_tester = SchemaTester()


class BaseAPITestCase(APITestCase):
    """ Base test class for api views including schema validation """

    @staticmethod
    def assertResponse(response: Response, **kwargs) -> None:
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

You can pass options either globally, when instantiating a `SchemaTester`, or locally, when
invoking `validate_response`:

```python
from openapi_tester import SchemaTester, is_camel_case
from tests.utils import my_uuid_4_validator

schema_test_with_case_validation = SchemaTester(
    case_tester=is_camel_case,
    ignore_case=["IP"],
    validators=[my_uuid_4_validator]
)

```

Or

```python
from openapi_tester import SchemaTester, is_camel_case
from tests.utils import my_uuid_4_validator

schema_tester = SchemaTester()


def my_test(client):
    response = client.get('api/v1/test/1')
    assert response.status_code == 200
    schema_tester.validate_response(
        response=response,
        case_tester=is_camel_case,
        ignore_case=["IP"],
        validators=[my_uuid_4_validator]
    )
```

### case_tester

The case tester argument takes a callable that is used to validate the key casings of both schemas and responses. If
nothing is passed, case validation is skipped.

The library currently has 4 built-in case testers:

- `is_pascal_case`
- `is_snake_case`
- `is_camel_case`
- `is_kebab_case`

You can of course pass your own custom case tester.

### ignore_case

List of keys to ignore when testing key casing. This setting only applies when case_tester is not `None`.

### validators

List of custom validators. A validator is a function that receives two parameters: schema_section and data, and returns
either an error message or `None`, e.g.:

```python
from typing import Any, Optional
from uuid import UUID


def my_uuid_4_validator(schema_section: dict, data: Any) -> Optional[str]:
    schema_format = schema_section.get("format")
    if schema_format == "uuid4":
        try:
            result = UUID(data, version=4)
            if not str(result) == str(data):
                return f"Expected uuid4, but received {data}"
        except ValueError:
            return f"Expected uuid4, but received {data}"
    return None
```

### field_key_map

You can pass an optional dictionary that maps custom url parameter names into values, for cases where this cannot be
inferred by the DRF `EndpointEnumerator`. A concrete use case for this option is when
the [django i18n locale prefixes](https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#language-prefix-in-url-patterns).

```python
from openapi_tester import SchemaTester

schema_tester = SchemaTester(field_key_map={
  "language": "en",
})
```

## Schema Validation

When the SchemaTester loads a schema, it runs it through
[OpenAPI Spec validator](https://github.com/p1c2u/openapi-spec-validator) which validates that the schema passes without
specification compliance issues. In case of issues with the schema itself, the validator will raise the appropriate
error.

## Known Issues

* We are using [prance](https://github.com/jfinkhaeuser/prance) as a schema resolver, and it has some issues with the
  resolution of (very) complex OpenAPI 2.0 schemas. If you encounter
  issues, [please document them here](https://github.com/snok/drf-openapi-tester/issues/205).

## Contributing

Contributions are welcome. Please see the [contributing guide](CONTRIBUTING.md)
