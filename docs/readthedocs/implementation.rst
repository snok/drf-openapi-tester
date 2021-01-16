.. _testing_with_openapi_tester:

**********************************
Implementing Django OpenAPI Tester
**********************************

This document contains an in-depth explanation on how the package works, and how to implement it.

Maintaining consistent and error-free documentation can be hard,
and it typically becomes exponentially harder as your documentation increases.
Response documentation in particular, is a combinatorial nightmare, as every API can have multiple methods,
where each method has multiple possible responses.

We suggest solving this problem by testing your response documentation against your actual API responses.
This way, you can *know* that your API responses match your documented responses.

Writing tests is as easy as appending a single line to your (hopefully) existing API tests.

Any inconsistencies between the API response received in the test, and the schema section that represents it, will raise an exception, causing the test to fail.

Examples
~~~~~~~~

**Pytest**

.. code:: python

    from openapi_tester.testing import validate_response

    def test_200_response_documentation(client):
        route = 'api/v1/test/1'
        response = client.get(route)

        assert response.status_code == 200
        assert response.json() == expected_response

        validate_response(response=response, method='GET', route=route)

**Django test**

.. code-block:: python

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

Error messages
~~~~~~~~~~~~~~

When found, errors will be raised in the following format:

.. code-block:: shell

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

- ``Expected`` describes the response data
- ``Received`` describes the schema.
- ``Hint`` will sometimes include a suggestion for what actions to take, to correct an error.
- ``Sequence`` will indicate how the response tester iterated through the data structure, before finding the error.

In this example, the response data is missing two attributes, ``height`` and ``width``, documented in the OpenAPI schema indicating that either the response needs to include more data, or that the OpenAPI schema should be corrected. It might be useful to highlight that we can't be sure whether the response or the schema is wrong; only that they are inconsistent.

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

The ``validate_response`` function takes three required inputs:

* response
    **description**: The response object returned from an API call.

    **type**: Response

    .. Note::

        Make sure to pass the response object, not the response data.

* method
    **description**: The HTTP method used to get the response.

    **type**: string

    **example**: ``method='GET'``


* route
    **description**: The resolvable path of your API.

    **type**: string

    **example**: ``route='api/v1/test'``


In addition, the function also takes two optional inputs:

* ignore_case
    **description**: List of keys for which we will skip case-validation. This can be useful for when you've made a conscious decision to, e.g., keep an acronym upper-cased although you have camelCase as a general standard.

    **type**: List of strings

    **example**: ``ignore_case=['API', 'IP]``

* verbose
    **description**: Whether to output more detailed error messages.

    **type**: bool

    **default**: ``False``

    **example**: ``verbose=True``


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

Case checking
=============

In addition to providing test functions for input and response validation,
the implements case checking on all documented property names when you run these functions.

``Case`` in this case, refers to which naming convention your project uses for its property names.
For example, it might use
`camelCase <https://en.wikipedia.org/wiki/Camel_case>`_,
`snake_case <https://en.wikipedia.org/wiki/Snake_case>`_,
or other related formats; the point being that once you settle on a convention,
it is important to remain consistent.

Ignoring Keys
-------------

These checks run as background processes in the package, and will raise errors when a suspected
mistake is caught.

If the package finds an inconsistency in your schema that *you would like to keep
as it is*, you can pass a list of the names you would like to ignore using ``ignore_case``.

One example of this could be if you are camel casing your
responses, but you prefer to keep an abbreviation fully capitalized::

    from openapi_tester.testing import validate_response

    ...

    validate_response(..., route='/api/v1/myApi/', ignore_case=['GUID', 'IP'])


Disabling Case Checks
---------------------

If you prefer not to check your documentations parameter names, you can set ``CASE_TESTER`` as ``None`` in the Django Swagger Tester settings.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg
