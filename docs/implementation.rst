.. _testing_with_django_swagger_tester:

**********************************
Implementing Django Swagger Tester
**********************************

This document contains a more in-depth explanation on how the package works, and how to implement it.

Response Validation
===================

Maintaining consistent and error-free documentation can be hard,
and it typically becomes exponentially harder as your documentation increases.
Response documentation in particular, is a combinatorial nightmare, as every API can have multiple methods,
where each method has multiple possible responses.

We suggest solving this problem by testing your response documentation against your actual API responses.
This way, you *know* that your API responses match your documented responses.

This makes it easy to catch and fix documentation errors proactively instead of reactively.

The package currently offers three alternative ways of achieving this:

- You can run response validation as a part of your test suite by manually writing tests
- You can implement live testing for your entire project, using the ``ResponseValidationMiddleware``
- You can implement live testing for a single API view, using the ``ResponseValidationView``

Static testing
--------------

Writing tests is as easy as appending a single line to your (hopefully) existing API tests.

Any inconsistencies between the API response received in the test, and the schema section that represents it, will raise an exception, causing the test to fail.

Examples
~~~~~~~~

**Pytest example**

.. code:: python

    from django_swagger_tester.testing import validate_response

    def test_200_response_documentation(client):
        route = 'api/v1/test/1'
        response = client.get(route)
        assert response.status_code == 200
        assert response.json() == expected_response

        # test swagger documentation
        validate_response(response=response, method='GET', route=route)

**Django test example**

.. code-block:: python

    from django_swagger_tester.testing import validate_response

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

            # test swagger documentation
            validate_response(response=response, method='GET', route=self.path)

Error messages
~~~~~~~~~~~~~~

When found, errors will be raised in the following format:

.. code-block:: shell

    django_swagger_tester.exceptions.SwaggerDocumentationError: Item is misspecified:

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

Live testing
------------

If you want to implement response validation for all outgoing API responses, you can use the ``ResponseValidationMiddleware``.

The middleware validates all outgoing ``APIView`` responses with the ``application/json`` content-type. Any errors/inconsistencies are then logged using a settings-specified log-level.

Implementing the middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply add the middleware to your settings.py

.. code:: python

    MIDDLEWARE = [
        ...
        'django_swagger_tester.middleware.ResponseValidationMiddleware',
    ]


Live testing individual views
-----------------------------

If you want to add live validation to an individual view, it is as simple as replacing your DRF ``APIView`` import with ``ResponseValidationView``.

The view class
~~~~~~~~~~~~~~

To be clear, the only difference between the DRF ``APIView`` and our view is that we've overwritten the ``finalize_response`` method to include response validation before returning the response from the view.

It's so simple we can show you the whole class here:

.. code:: python

    class ResponseValidationView(APIView):
        def finalize_response(self, request, response, *args, **kwargs):
            """
            Adds response validation to the end of the original method.
            """
            response = super(ResponseValidationView, self).finalize_response(
                request, response, *args, **kwargs
            )
            if settings.view_settings.response_validation.debug:
                response.render()
                copied_response = copy_response(response)
                safe_validate_response(
                    response=copied_response,
                    path=request.path,
                    method=request.method,
                    func_logger=settings.view_settings.response_validation.logger,
                )
            return response

Example
~~~~~~~

An example view could look like this:

.. code:: python

    from rest_framework.status import HTTP_200_OK

    from django_swagger_tester.views import ResponseValidationView


    class Animals(ResponseValidationView):  # <-- add the view class here here
        def get(self, request, version: int):
            animals = {
                'dog': 'very cool',
                'monkey': 'very cool',
                'bird': 'mixed reviews',
            }
            return Response(animals, HTTP_200_OK)



Input Validation
================

As with your response documentation, it can be useful to test your
request body documentation to ensure it is, and remains, accurate.

To use the ``validate_input_serializer`` tester, you must be using Django Rest Framework's ``Serializer`` for input validation.

Example
-------

.. code-block:: python

    from myapp.api.serializers import MySerializer
    from django_swagger_tester.testing import validate_input_serializer


    def test_request_body_documentation(client):
        """
        Verifies that our request body documentation is representative of a valid request body.
        """
        validate_input_serializer(serializer=MySerializer, method='POST', route='api/v1/test/', camel_case_parser=True)

.. Note::

    The ``camel_case_parser`` argument can be set to ``True`` if your DRF API uses
    `djangorestframework-camel-case <https://github.com/vbabiy/djangorestframework-camel-case>`_'s
    ``CamelCaseJSONParser`` or ``CamelCaseJSONRenderer``. The ``camel_case_parser`` keyword argument defaults to False, unless you've set ```CAMEL_CASE_PARSER`` to True in the package setting.

validate_input_serializer
-------------------------

The ``validate_input_serializer`` function takes three required inputs:

* serializer
    **description**: The Serializer object used for validating API inputs.

    **type**: rest_framework.serializer.Serializer

* method
    **description**: The HTTP method used to get the response.

    **type**: string

    **example**: ``method='GET'``

* route
    **description**: The resolvable path of your API.

    **type**: string

    **example**: ``route='api/v1/test'``


In addition, the function also takes one optional input:

* camel_case_parser
    **description**: Whether or not to convert a camel-cased example to snake case before passing it to your serializer.

    **type**: boolean

    **example**: ``camel_case_parser=True``

.. Note::

    The ``CAMEL_CASE_PARSER`` project setting lets you specify a project-wide default for the ``camel_case_parser`` argument.

    See `configuration <configuration.html#camel-case-parser>`_ for more info.


Suggested Use
-------------

If you have a file for tests related to each view, input validation tests can be added to each file individually, like we would reccomend you do with response validation tests.
However, input validation tests are also well suited to live separately from your API view tests, because they do not require a database or a request client.

This allows you to put all your input tests into one file. This enables you to very simply test a whole suite of endpoints with very little code::

    from django.test import SimpleTestCase
    from django_swagger_tester.testing import validate_input_serializer

    from api.serializers.validation.request_bodies import ValidateDeleteOrderBody, ...


    class TestSwaggerInput(SimpleTestCase):
        endpoints = [
            {
                'api/v1/orders/': [
                    ('POST', ValidatePostOrderBody),
                    ('PUT', ValidatePutOrderBody),
                    ('DELETE', ValidateDeleteOrderBody)
                ]
            },
            {
                'api/v1/orders/<id>/entries/': [
                    ('POST', ValidatePostEntryBody),
                    ('PUT', ValidatePutEntryBody),
                    ('DELETE', ValidateEntryDeleteBody)
                ]
            },
        ]

        def test_swagger_input(self) -> None:
            """
            Verifies that the documented request bodies are valid.
            """
            for endpoint in self.endpoints:
                for route, values in endpoint.items():
                    for method, serializer in values:
                        validate_input_serializer(serializer=serializer, method=method, route=route)


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

    from django_swgger_tester.testing import validate_response

    ...

    validate_response(..., route='/api/v1/myApi/', ignore_case=['GUID', 'IP'])


Disabling Case Checks
---------------------

If you prefer not to check your Swagger docs' parameter names, you can set ``CASE`` as ``None`` in the Django Swagger Tester settings.

.. _Drf_yasg: https://github.com/axnsan12/drf-yasg
