import logging
from typing import Optional

from django.core.exceptions import MultipleObjectsReturned

from django_swagger_tester.models import Method, Schema, Url, ValidatedResponse
from django_swagger_tester.utils import resolve_path

logger = logging.getLogger('django_swagger_tester')


def save_validated_response(
    path: str,
    method: str,
    response_hash: str,
    schema_hash: str,
    valid: bool,
    status_code: int,
    error_message: Optional[str] = None,
) -> ValidatedResponse:
    """
    Creates a ValidatedResponse object.
    """
    # we need to save the deparameterized path (/api/{version}/{vehicle_type}/correct)
    # and not the path (/api/v1/cars/correct)
    # otherwise we will get a new DB-entry for every `id` in a /api/v1/resource/{id}-endpoint, which defeats the purpose
    deparameterized_path, resolved_path = resolve_path(path)

    logger.info('Saving %s response from %s request to `%s`', 'valid' if valid else 'invalid', method, path)
    url, _ = Url.objects.get_or_create(url=deparameterized_path)
    method, _ = Method.objects.get_or_create(method=method)
    try:
        schema, _ = Schema.objects.get_or_create(hash=str(schema_hash))
    except MultipleObjectsReturned:
        schema = Schema.objects.filter(hash=str(schema_hash)).first()
    return ValidatedResponse.objects.create(
        method=method,
        url=url,
        schema_hash=schema,
        response_hash=str(response_hash),
        valid=valid,
        status_code=status_code,
        error_message=error_message,
    )


def get_validated_response(path: str, method: str, response_hash: str) -> ValidatedResponse:
    """
    Fetches a ValidatedResponse object.
    """
    deparameterized_path, resolved_path = resolve_path(path)
    return ValidatedResponse.objects.prefetch_related('schema_hash').get(
        url__url=deparameterized_path, method__method=method, response_hash=str(response_hash)
    )
