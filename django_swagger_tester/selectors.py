from typing import Optional

from django_swagger_tester.models import Method, Schema, Url, ValidatedResponse


def save_validated_response(
    path: str, method: str, response_hash: str, schema_hash: str, valid: bool, error_message: Optional[str] = None
) -> ValidatedResponse:
    """
    Creates a ValidatedResponse object.
    """
    url, _ = Url.objects.get_or_create(url=path)
    method, _ = Method.objects.get_or_create(url=url, method=method)
    schema, _ = Schema.objects.get_or_create(hash=str(schema_hash))
    return ValidatedResponse.objects.create(
        method=method, schema_hash=schema, response_hash=str(response_hash), valid=valid, error_message=error_message
    )


def get_validated_response(path: str, method: str, response_hash: str) -> ValidatedResponse:
    """
    Fetches a ValidatedResponse object.
    """
    return ValidatedResponse.objects.prefetch_related('schema_hash').get(
        method__url__url=path, method__method=method, response_hash=str(response_hash)
    )
