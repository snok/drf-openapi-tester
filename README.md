<p align="center">
  <a><img width="750px" src="docs/img/readme_logo4.png" alt='logo'></a>
</p>

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

---

**Documentation**: [https://django-swagger-tester.readthedocs.io/](https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest)

**Repository**: [https://github.com/sondrelg/django-swagger-tester](https://github.com/sondrelg/django-swagger-tester)

---

# Django Swagger Tester

This package is a utility for testing Django Swagger documentation, with the goal of making it easy for developers to spot documentation errors.

### Features
The package has three main features:

- [Testing response documentation](https://django-swagger-tester.readthedocs.io/en/latest/testing_with_django_swagger_tester.html#response-validation)

- [Testing input documentation](https://django-swagger-tester.readthedocs.io/en/latest/testing_with_django_swagger_tester.html#input-validation)

- [Ensuring all documentation complies with a single parameter naming standard](https://django-swagger-tester.readthedocs.io/en/latest/testing_with_django_swagger_tester.html#case-checking).

    Supported naming standards include `camelCase`, `snake_case`, `kebab-case`, and `PascalCase`.

### Supported Implementations

- Dynamically rendered documentation, using [drf_yasg](https://github.com/axnsan12/drf-yasg)'s `get_schema_view`
- Any implementation rendered from OpenAPI schema file (yaml/json)

If you're using another method to generate your documentation and would like to use this library, feel free to add an issue, or create a PR.

## Installation

Install using pip:

```python
pip install django-swagger-tester
```


## Configuration


### Settings


To add Django Swagger Settings in your project, add a ``SWAGGER_TESTER`` object to your ``settings.py``:

```python
SWAGGER_TESTER = {
    'CASE': 'camel case',
    'PATH': BASE_DIR + '/openapi-schema.yml'  # not required for drf_yasg implementations
}
```

### Setting parameters

* CASE
    The case standard you wish to enforce for your documentation.

    Needs to be one of the following:

    * `camel case`
    * `snake case`
    * `pascal case`
    * `kebab case`
    * `None`

    Your OpenAPI schema will be assessed to make sure all parameter names are correctly cased according to this preference.
    If you do not wish to enforce this check, you can specify `None` to skip this feature.

    Example:

    ```python
    SWAGGER_TESTER = {
        'CASE': 'snake case',
    }
    ```

    Default: `camel case`

* PATH
    The path to your OpenAPI specification.

    Example:

    ```python
    SWAGGER_TESTER = {
        'PATH': BASE_DIR + '/openapi-schema.yml',
    }
    ```

    *This setting is not required if your swagger docs are generated.*


## Implementation

For a full explanation of how to use this package, please see the [docs](https://django-swagger-tester.readthedocs.io/).

### Response validation

To verify that your API response documentation is correct, we suggest testing the generated documentation against an actual API response.

#### The validate_response function

The ``validate_response`` function takes three required inputs:

* response
    description: This should be the response object returned from an API call. Note: Make sure to pass the response object, not the response data, as we need to match both ``status_code`` and ``json`` to the OpenAPI schema.
    type: Response

* method
    description: This should be the HTTP method used to get the response.
    type: string
    example: 'GET'

* endpoint_url
    description: This should be the resolvable path of your endpoint.
    type: string
    example: 'api/v1/test'

In addition, the function also takes one optional input:

* ignore_case
    description: List of keys for which we will skip case-validation. This can be useful for when you've made a conscious decision to, e.g., keep an acronym upper-cased although you have camelCase as a general standard.
    type: list of strings
    example: ['API',]

#### drf_yasg

The drf_yasg tester is be imported from its own project folder:

```python
from django_swagger_tester.drf_yasg import validate_response
```

#### Statically rendered docs

When testing a static schema (located locally in your project), make sure to point to the right file in the ``PATH`` setting.

The static schema implementation can be imported from its own project folder:

```python
from django_swagger_tester.static_schema import validate_response
```

#### Examples

A pytest implementation might look like this:

```python
def test_response_documentation(client):
    response = client.get('api/v1/test/')

    assert response.status_code == 200
    assert response.json() == expected_response

    # Test Swagger documentation
    validate_response(response=response, method='GET', route='api/v1/test/', ignore_case=[])
```

A Django-test implementation might look like this:

```python
class MyApiTest(APITestCase):

    def setUp(self) -> None:
        user, _ = User.objects.update_or_create(username='test_user')
        self.client.force_authenticate(user=user)
        self.path = '/api/v1/test/'

    def test_get_200(self) -> None:
        """
        Verifies that a 200 is returned for a valid GET request to the /test/ endpoint.
        """
        response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
        expected_response = [...]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        # Test Swagger documentation
        validate_response(response=response, method='GET', route=self.path, ignore_case=[])
```

You can also test more than a single response at the time:

```python
def test_response_documentation(client):
    # 201 - Resource created
    response = client.post('api/v1/test/', data=...)
    validate_response(response=response, method='POST', route='api/v1/test/', ignore_case=[])

    # 200 - Idempotency --> if an object exists, return it with a 200 without creating a new resource
    response = client.post('api/v1/test/', data=...)
    validate_response(response=response, method='POST', route='api/v1/test/', ignore_case=[])

    # 400 - Bad data
    response = client.post('api/v1/test/', data=bad_data)
    validate_response(response=response, method='POST', route='api/v1/test/', ignore_case=[])
```


### Input validation

Similarly to the response documentation, request body examples should be representative of a functioning request body. If you use Django Rest Framework's `Serializer` class for input validation, it is simple to make sure that all your documented request bodies would pass input validation for all endpoints.

This is currently under development and will be added for v1.0.0
