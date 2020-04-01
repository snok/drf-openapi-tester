import pytest

from django_swagger_tester.response_validation.base.base import SwaggerTestBase

base = SwaggerTestBase()


class MockResponse:

    @staticmethod
    def json():
        return {'test': 'test'}


response = MockResponse()
response.status_code = 200


def test_successful_unpack():
    """
    This should run without errors.
    """
    base._unpack_response(response)
    assert base.data == {'test': 'test'}
    assert base.status_code == 200


def test_unsuccesful_unpack():
    """
    Verify that the appropriate error is raised when unpack fails.
    """

    def _raise_exception():
        raise Exception('test')

    response.json = _raise_exception
    with pytest.raises(Exception, match='Unable to unpack response object. Make sure you are passing response, and not response.json()'):
        base._unpack_response(response)
