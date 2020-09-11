import pytest

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.testing import validate_response


def test_endpoints_bad_case(client) -> None:  # noqa: TYP001
    """
    Asserts bad case errors are raised correctly in the tester.
    """
    response = client.get('/api/v1/snake-case/')
    assert response.status_code == 200

    # Test Swagger documentation
    with pytest.raises(
        SwaggerDocumentationError, match='The response key `this_is_snake_case` is not properly camelCased'
    ):
        validate_response(response=response, method='GET', route='/api/v1/snake-case')  # type: ignore
