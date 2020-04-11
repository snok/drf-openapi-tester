import pytest

from django_swagger_tester.utils import unpack_response


class MockResponse:
    status_code = 200

    @staticmethod
    def json():
        return {'test': 'test'}


response = MockResponse()
response.status_code = 200


def test_successful_unpack():
    """
    This should run without errors.
    """
    data, status_code = unpack_response(response)
    assert data == {'test': 'test'}
    assert status_code == 200


def test_unsuccesful_unpack():
    """
    Verify that the appropriate error is raised when unpack fails.
    """

    def _raise_exception():
        raise Exception('test')

    response.json = _raise_exception
    with pytest.raises(Exception, match='Unable to unpack response object. Make sure you are passing response, and not response.json()'):
        unpack_response(response)
