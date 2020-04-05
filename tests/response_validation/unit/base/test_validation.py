import pytest

from django_swagger_tester.response_validation.base.base import SwaggerTestBase

base = SwaggerTestBase()


def test_validation():
    """
    Validation should do nothing, so not sure how to test this properly. Leaving this as a placeholder.
    """
    assert base.validation() is None

    with pytest.raises(TypeError, match='takes 1 positional argument but 2 were given'):
        base.validation(2)
