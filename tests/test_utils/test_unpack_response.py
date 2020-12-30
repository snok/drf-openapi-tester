import pytest

from django_openapi_response_tester.utils import unpack_response


def test_successful_unpack():
    """
    This should run without errors.
    """

    class MockResponse:
        status_code = 200

        @staticmethod
        def json():
            return {'test': 'test'}

    response = MockResponse()
    response.status_code = 200

    data, status_code = unpack_response(response)
    assert data == {'test': 'test'}
    assert status_code == 200


def test_bad_json_method():
    """
    Verify that the appropriate error is raised when unpack fails.
    """

    class NonJsonMockResponse:
        status_code = 204

    response = NonJsonMockResponse()

    with pytest.raises(
        Exception,
        match='Response does not contain a JSON-formatted response and cannot be tested against a response schema.',
    ):
        unpack_response(response)


def test_bad_status_code():
    """
    Verify that the appropriate error is raised when we cannot access status_code.
    """

    class NonJsonMockResponse:
        pass

    response = NonJsonMockResponse()

    with pytest.raises(
        Exception,
        match='Response object does not contain a status code. Unable to unpack response object.',
    ):
        unpack_response(response)
