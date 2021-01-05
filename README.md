
<p align="center"><h1 align='center'>Django OpenAPI Tester</h1></p>
<p align="center">
    <em>A test utility for validating API responses</em>
</p>
<p align="center">
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/pypi/v/django-swagger-tester.svg" alt="Package version">
    </a>
    <a href="https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest" alt="Documentation status">
    </a>
    <a href="https://codecov.io/gh/snok/django-openapi-tester">
        <img src="https://codecov.io/gh/snok/django-openapi-tester/branch/master/graph/badge.svg" alt="Code coverage">
    </a>
    <a href="https://pypi.org/project/django-openapi-tester/">
        <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Supported Python versions">
    </a>
    <a href="https://pypi.python.org/pypi/django-openapi-tester">
        <img src="https://img.shields.io/badge/django%20versions-2.2%2B-blue" alt="Supported Django versions">
    </a>
    <a href="http://mypy-lang.org/">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
    </a>
</p>

--------------

**Documentation**: [https://django-swagger-tester.readthedocs.io](https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest)

**Repository**: [https://github.com/snok/django-openapi-tester](https://github.com/snok/django-openapi-tester)

--------------

Django OpenAPI Tester is a simple test utility. Its aim is to make it easy for
developers to catch and correct documentation errors in their OpenAPI schema.

Maintaining good documentation can be pretty boring, and proof reading your docs
to make sure they're actually describing your API is worse.
By simply testing that your API responses match your schema definitions you can
*know* that your schema reflects reality.

To illustrate; given this example response:

```python
{
    "id": 0,
    "name": "doggie",
    "status": "available",
    "photoUrls": ["string"],
    "tags": [{"id": 0, "name": "string"}],
    "category": {"id": 0, "name": "string"},
}
```

your brain shouldn't have to manually scan this response
schema for errors..

```yaml
responses:
  '200':
    description: successful operation
    schema:
      type: object
      required:
      - name
      - photoUrls
      properties:
        id:
          type: integer
          format: int64
        category:
          type: object
          properties:
            id:
              type: integer
              format: int64
            name:
              type: string
          xml:
            name: Category
        name:
          type: string
          example: doggie
        photoUrl:
          type: array
          xml:
            wrapped: true
          items:
            type: string
            xml:
              name: photoUrl
        tags:
          type: array
          xml:
            wrapped: true
          items:
            type: object
            properties:
              id:
                type: integer
                format: int64
              name:
                type: string
            xml:
              name: Tag
        status:
          type: string
          description: pet status in the store
          enum:
          - available
          - pending
          - sold
      xml:
        name: Pet
```

..when automated tests can simply tell you that ``photoUrls`` is missing an ``s``.

Not only that, but when you come back and change your API next year, your test
suite should not allow you to deploy your changes without remembering to
update your documentation.

## Implementations

This package currently supports:

- Testing of dynamically rendered OpenAPI schemas using [drf-yasg](https://github.com/axnsan12/drf-yasg)
- Testing of dynamically rendered OpenAPI schemas using [drf-spectacular](https://github.com/tfranzel/drf-spectacular)
- Testing any implementation which generates a static yaml or json file (e.g., like [DRF](https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas))

If you're using another method to generate your documentation and would like to use this package, feel free to add an issue, or create a PR. Adding a new implementation is as easy as adding the required logic needed to load the OpenAPI schema.

## Installation

Install using pip:

```shell script
pip install django-openapi-tester
```


## Settings

To use the package in your project, you first need to configure the package
settings in your ``settings.py``.

At minimum we need to know schema loader class to use to load your OpenAPI schema:

```python
from openapi_tester.loaders import StaticSchemaLoader

OPENAPI_TESTER = {
    'SCHEMA_LOADER': StaticSchemaLoader,
}
```

See the [configuration](https://django-swagger-tester.readthedocs.io/en/latest/configuration.html) section of the docs for more info.


## Response Validation


### Testing with Pytest

```python
from openapi_tester.testing import validate_response

def test_200_response_documentation(client):
    route = 'api/v1/test/1'
    response = client.get(route)

    assert response.status_code == 200
    assert response.json() == expected_response

    validate_response(response=response, method='GET', route=route)
```

### Testing with Django Test

```python
from openapi_tester.testing import validate_response

class MyApiTest(APITestCase):

    path = '/api/v1/test/'

    def setUp(self) -> None:
        user, _ = User.objects.update_or_create(username='test_user')
        self.client.force_authenticate(user=user)

    def test_get_200(self) -> None:
        """
        Verifies that a 200 is returned for a valid GET request to the /test/ endpoint.
        """
        response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
        expected_response = [...]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        validate_response(response=response, method='GET', route=self.path)
```

### Error messages

When found, errors will be raised in the following format:

```shell script
openapi_tester.exceptions.SwaggerDocumentationError: Item is misspecified:

Summary
-------------------------------------------------------------------------------------------

Error:      The following properties seem to be missing from your response body: length, width.

Expected:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}
Received:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'}

Hint:       Remove the key(s) from you Swagger docs, or include it in your API response.
Sequence:   init.list

-------------------------------------------------------------------------------------------

* If you need more details: set `verbose=True`
```

- `Expected` describes the response data
- `Received` describes the schema.
- `Hint` will sometimes include a suggestion for what actions to take, to correct an error.
- `Sequence` will indicate how the response tester iterated through the data structure, before finding the error.

In this example, the response data is missing two attributes, ``height`` and ``width``, documented in the OpenAPI schema indicating that either the response needs to include more data, or that the OpenAPI schema should be corrected. It might be useful to highlight that we can't be sure whether the response or the schema is wrong; only that they are inconsistent.

---------

For more info see the [docs](https://django-swagger-tester.readthedocs.io/en/latest/)
