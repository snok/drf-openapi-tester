import pytest

from response_tester.utils import type_placeholder_value


def test_type_placeholder_value():
    assert type_placeholder_value("boolean") == True  # noqa: E712
    assert type_placeholder_value("integer") == 1
    assert type_placeholder_value("number") == 1.0
    assert type_placeholder_value("string") == "string"
    assert type_placeholder_value("file") == "string"


def test_bad_type():
    with pytest.raises(TypeError, match="Cannot return placeholder value for test"):
        type_placeholder_value("test")
