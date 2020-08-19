# noqa: TYP001
import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.case_testers import is_camel_case, is_kebab_case, is_pascal_case, is_snake_case
from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_settings


def test_valid_cases(monkeypatch) -> None:  # noqa: TYP001
    """
    Assert that valid cases always pass without errors.
    """
    for case in [
        is_snake_case,
        is_camel_case,
        is_pascal_case,
        is_kebab_case,
        lambda x: x * 2,  # custom callable
        None,
    ]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_TESTER', case))
        SwaggerTesterSettings()


def test_invalid_cases(monkeypatch) -> None:
    """
    Asserts that any invalid case raises an appropriate error.
    """
    for case in ['snakecase', 1, {}]:
        monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_settings('CASE_TESTER', case))
        with pytest.raises(
            ImproperlyConfigured,
            match=(
                'The django-swagger-tester CASE_TESTER setting is misspecified. '
                'Please pass a case tester callable from django_swagger_tester.case_testers, '
                'make your own, or pass `None` to skip case validation.'
            ),
        ):
            SwaggerTesterSettings()
