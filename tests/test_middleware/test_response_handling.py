import pytest
from django.core.exceptions import ImproperlyConfigured


def test_request_with_no_correlation_id(client, caplog):
    """
    Makes sure that a response containing a uuid4 value doesn't throw a SwaggerDocumentationError when checked with
    the middleware.

    A returned uuid4 will be parsed as a string when unpacking a response.json(), but in the middleware, this is not the case
    if you use response.data. We've added logic to correct this difference, and this test is in place to make sure we
    dont break that logic.
    """
    response = client.post('/api/v1/items', data={'itemType': 'bicycle'})
    print(response)
    # expected = [
    #     (
    #         'Header `Correlation-ID` was not found in the incoming request. Generated new GUID: 704ae5472cae4f8daa8f2cc5a5a8mock',
    #         None,
    #     ),
    #     ('This log message should have a GUID', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    #     ('Some warning in a function', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    #     ('Received signal `request_finished`', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    #     ('Deleting 704ae5472cae4f8daa8f2cc5a5a8mock from _guid', '704ae5472cae4f8daa8f2cc5a5a8mock'),
    # ]
    # assert [(x.message, x.correlation_id) for x in caplog.records] == expected
    # assert response['Correlation-ID'] == '704ae5472cae4f8daa8f2cc5a5a8mock'
