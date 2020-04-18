.. _testing_with_django_swagger_tester:

**********************************
Testing with django Swagger Tester
**********************************

This document contains an in-depth explanation on how the package works, and how to best implement it.

Response validation
===================

An OpenAPI schema should generally span all APIs you provide. For each API, there may be several methods to document (GET, PUT, POST, DELETE, ...), and for each method you may have several responses (200, 400, 401, 404, 5XX). Seeing that at least parts of the OpenAPI schema used for rendering your swagger docs will need to be maintained manually, it is easy to see how bugs might be introduced in the documentation over time. By testing your response documentation against your actual API responses, you can make sure that errors don't pass silently.

This functionality is currently compatible with rendered static schema, or generated `drf_yasg`_ swagger docs.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg

At the core, the logic for testing an OpenAPI schema is the same, regardless of your Swagger implementation. However, because packages like drf_yasg_ lets you generate documentation on the fly, we need custom logic for extracting the schema. The result is that we need separate implementations for separate documentation implementations, simply for loading schemas.

The validate_response function
------------------------------

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

Dynamically rendered OpenAPI schema with drf_yasg
-------------------------------------------------

The drf_yasg_ implementation can be imported from its own project folder:

.. code-block:: python

    from django_swagger_tester.drf_yasg import validate_response


Statically rendered OpenAPI schema
----------------------------------

When testing a static schema (located locally in your project), make sure to point to the right file in the ``PATH`` setting.

The static schema implementation can be imported from its own project folder:

.. code-block:: python

    from django_swagger_tester.response_validation.static_schema import validate_response


Examples
--------

A pytest implementation might look like this:

.. code:: python

    def test_response_documentation(client):
        response = client.get('api/v1/test/')

        assert response.status_code == 200
        assert response.json() == expected_response

        # Test Swagger documentation
        validate_response(response=response, method='GET', endpoint_url='api/v1/test/', ignore_case=[])

A Django-test implementation might look like this:

.. code-block:: python

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
            validate_response(response=response, method='GET', endpoint_url=self.path)

You can also test more than a single response at the time.

.. code:: python

    def test_response_documentation(client):
        # 201 - Resource created
        response = client.post('api/v1/test/', data=...)
        validate_response(response=response, method='POST', endpoint_url='api/v1/test/', ignore_case=[])

        # 200 - Idempotency --> if an object exists, return it with a 200 without creating a new resource
        response = client.post('api/v1/test/', data=...)
        validate_response(response=response, method='POST', endpoint_url='api/v1/test/', ignore_case=[])

        # 400 - Bad data
        response = client.post('api/v1/test/', data=bad_data)
        validate_response(response=response, method='POST', endpoint_url='api/v1/test/', ignore_case=[])

Input validation
================

Similarly to the response documentation, request body examples should be representative of a functioning request body. If you use Django Rest Framework's `Serializer` class for input validation, it is simple to make sure that all your documented request bodies would pass input validation for all endpoints.

This is currently under development and will be added for v1.0.0

Case checking
=============

Documentation inconsistencies can be hard to catch when maintaining more than two APIs, let alone hundreds. As a part of the documentation validators mentioned above, this package also implements case checking on all documented property names.

``Case`` in this case, refers to which naming convention your project uses for its property names.
For example, it might use
`camelCase <https://en.wikipedia.org/wiki/Camel_case>`_,
`snake_case <https://en.wikipedia.org/wiki/Snake_case>`_,
or other related formats; the point being that, once you settle on a convention,
it is important to remain consistent.

These checks run as background processes in the package, and will raise errors when a suspected
mistake is caught. If the package finds an inconsistency in your schema that *you would like to keep
as it is*, you can pass a list of the names you would like to ignore using `ignore_case` as a key
word argument to the validator you're using. One example of this could be if you are camel casing your
responses, but you prefer to keep an abbreviation fully capitalized::

    from django_swgger_tester.drf_yasg import validate_response

    ...

    validate_response(response=response, method='GET', route='/api/v1/myApi/', ignore_case=['GUID', 'IP'])
