import pytest

from django_swagger_tester.response_validation.base.base import SwaggerTestBase

base = SwaggerTestBase()


def test_load_schema():
    """
    Validation should do nothing, so not sure how to test this properly. Leaving this as a placeholder.
    """
    assert base.load_schema() is None

    with pytest.raises(TypeError, match='takes 1 positional argument but 2 were given'):
        base.load_schema(2)
