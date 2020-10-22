import logging
from typing import Callable

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response

from django_swagger_tester.exceptions import CaseError, SwaggerDocumentationError, UndocumentedSchemaSectionError
from django_swagger_tester.selectors import get_validated_response, save_validated_response
from django_swagger_tester.utils import format_response_tester_error, hash_response, hash_schema

logger = logging.getLogger('django_swagger_tester')


def clear_cache() -> None:
    """
    Deletes all cached responses and response schemas.
    """
    from django_swagger_tester.models import Schema, ValidatedResponse

    ValidatedResponse.objects.all().delete()
    Schema.objects.all().delete()


def safe_validate_response(response: Response, path: str, method: str, func_logger: Callable) -> None:
    """
    Validates an outgoing response object against the OpenAPI schema response documentation.

    In case of inconsistencies, a log is logged at a setting-specified log level.

    Unlike the django_swagger_tester.testing validate_response function,
    this function should *not* raise any errors during runtime.

    :param response: HTTP response
    :param path: The request path
    :param method: The request method
    :param func_logger: A logger callable
    """
    logger.info('Validating response for %s request to %s', method, path)
    from django_swagger_tester.configuration import settings

    try:
        # load the response schema
        response_schema = settings.loader_class.get_response_schema_section(
            route=path,
            status_code=response.status_code,
            method=method,
            skip_validation_warning=True,
        )
        schema_hash = hash_schema(response_schema)
    except UndocumentedSchemaSectionError as e:
        if response.status_code == 204:
            return
        func_logger(
            'Failed accessing response schema for %s request to `%s` with status %s. Is the endpoint '
            'documented? Error: %s',
            method,
            path,
            response.status_code,
            e,
        )
        return

    # define extra parameters to add to error logs
    logger_extra = {
        # `dst` is added in front of the extra attrs to make the attribute names more unique,
        # to avoid naming collisions - naming collisions can be problematic in, e.g., elastic
        # if the two colliding logs contain different variable types for the same attribute name
        'dst_response_schema': str(response_schema),
        'dst_response_data': str(response.data),
        'dst_case_tester': settings.case_tester.__name__ if settings.case_tester.__name__ != '<lambda>' else 'n/a',
        'dst_camel_case_parser': str(settings.camel_case_parser),
    }

    # See if we've validated this response in the past
    response_hash = hash_response(response.data)
    try:
        obj = get_validated_response(path, method, str(response_hash))
        if str(obj.schema_hash.hash) != str(schema_hash):
            logger.info('Clearing cache')
            clear_cache()
        elif not obj.valid:
            logger.info(
                'Found response hash in DB. Response already checked and is invalid. Re-logging error from cache.'
            )
            # re-log the error if the response validation failed, and schema hasn't changed
            # this can "spam" a system with errors, but that can actually be quite useful for drawing attention to the problem
            # in solutions like Sentry
            settings.view_settings.response_validation.logger(obj.error_message, extra=logger_extra)
            return
        else:
            # if object is valid, and the schema is unchanged, there is no reason to re-run validation
            logger.info('Found response hash in DB. Response already checked and is valid.')
            return
    except ObjectDoesNotExist:
        pass

    try:
        # validate response data with respect to response schema
        from django_swagger_tester.schema_tester import SchemaTester

        SchemaTester(
            schema=response_schema,
            data=response.data,
            case_tester=settings.case_tester,
            camel_case_parser=settings.camel_case_parser,
            origin='response',
        )
        logger.info('Response valid for %s request to %s', method, path)
        save_validated_response(
            path, method, response_hash, schema_hash, valid=True, status_code=response.status_code, error_message=None
        )
    except SwaggerDocumentationError as e:
        long_message = format_response_tester_error(e, hint=e.response_hint, addon='')
        error_message = f'Bad response returned for {method} request to {path}. Error: {long_message}'
        func_logger(error_message, extra=logger_extra)
        save_validated_response(
            path,
            method,
            response_hash,
            schema_hash,
            valid=False,
            status_code=response.status_code,
            error_message=error_message,
        )
    except CaseError as e:
        error_message = f'Found incorrectly cased cased key, `{e.key}` in {e.origin}'
        func_logger(error_message, extra=logger_extra)
        save_validated_response(
            path,
            method,
            response_hash,
            schema_hash,
            valid=False,
            status_code=response.status_code,
            error_message=error_message,
        )
    except Exception as e:
        logger.error(
            'Error raised unexpectedly. If this happens, please report it here: '
            '`https://github.com/snok/django-swagger-tester/issues/new`. Error: %s',
            e,
        )
