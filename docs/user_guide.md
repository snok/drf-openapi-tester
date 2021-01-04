# Testing your response documentation

Adding tests to verify your response documentation can
be as easy as appending a single line to your (hopefully)
existing API tests.

If any we find any inconsistency between the API JSON
response and the documented response in your OpenAPI
schema, we raise an exception, causing your test to fail.

## Test examples

### Pytest examples

```python
    from openapi_tester.testing import validate_response

    def test_200_response_documentation(client):
        route = 'api/v1/test/1'
        response = client.get(route)

        assert response.status_code == 200
        assert response.json() == expected_response

        # Add this line to your API tests
        validate_response(response=response, method='GET', route=route)
```

### Django test example

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

            # Add this line to your API tests
            validate_response(response=response, method='GET', route=self.path)
```

## Error messages

When found, errors will be formatted as follows:

```shell script
openapi_tester.exceptions.DocumentationError: Item is misspecified:

Summary
-------------------------------------------------------------------------------------------

Error:      The following properties seem to be missing from your response body: length, width.

Expected:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}
Received:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'}

Hint:       Remove the key(s) from your OpenAPI docs, or include it in your API response.
Sequence:   init.list

-------------------------------------------------------------------------------------------

* If you need more details: set `verbose=True`
```

- `Expected` describes the response data
- `Received` describes the schema.
- `Hint` will sometimes include a suggestion for what actions to take, to correct an error.
- `Sequence` will indicate how the response tester iterated through the data structure, before finding the error.

In this example, the response data is missing two attributes, `height` and `width`, documented in the OpenAPI schema indicating that either the response needs to include more data, or that the OpenAPI schema should be corrected. It might be useful to highlight that we can't be sure whether the response or the schema is wrong; only that they are inconsistent.

.. Note::

    It can be useful to test more than just successful responses::

        def test_post_endpoint_responses(client):
            # 201 - Resource created
            response = client.post(...)
            validate_response(response=response, method='POST', route='api/v1/test/')

            # 400 - Bad data
            response = client.post(...)
            validate_response(response=response, method='POST', route='api/v1/test/')

        def test_get_endpoint_responses(client):
            # 200 - Fetch resource
            response = client.get(...)
            validate_response(response=response, method='GET', route='api/v1/test/<id>')

            # 404 - Bad ID
            response = client.get(...)
            validate_response(response=response, method='GET', route='api/v1/test/<bad id>')



The validate_response function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `validate_response` function takes three required inputs:

* response
    **description**: The response object returned from an API call.

    **type**: Response

    .. Note::

        Make sure to pass the response object, not the response data.

* method
    **description**: The HTTP method used to get the response.

    **type**: string

    **example**: `method='GET'`


* route
    **description**: The resolvable path of your API.

    **type**: string

    **example**: `route='api/v1/test'`


In addition, the function also takes two optional inputs:

* ignore_case
    **description**: List of keys for which we will skip case-validation. This can be useful for when you've made a conscious decision to, e.g., keep an acronym upper-cased although you have camelCase as a general standard.

    **type**: List of strings

    **example**: `ignore_case=['API', 'IP]`

* verbose
    **description**: Whether to output more detailed error messages.

    **type**: bool

    **default**: `False`

    **example**: `verbose=True`


Suggested use
~~~~~~~~~~~~~

The response validation function can be called from anywhere,
but because the tests require a request client it generally makes sense to include
these tests with your existing API view tests.

For example::

    class TestGetCustomers(AuthorizedRequestBase):

        ...

        def test_is_valid(self):
            """
            Verify that we get a 200 from a valid request.
            """
            response = self.get(route='api/v1/customers/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

        def test_swagger_schema(self):
            """
            Verifies that the API response matches the swagger documentation for the endpoint.
            """
            response = self.get(route='api/v1/customers/')
            validate_response(response=response, method='GET', route='api/v1/customers/')

        ...
