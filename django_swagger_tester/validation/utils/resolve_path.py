import difflib
import logging


logger = logging.getLogger('django_swagger_tester')


def resolve_path(endpoint_path: str) -> tuple:
    """
    Resolves a Django path.
    """
    from django.urls import Resolver404, resolve

    try:
        logger.debug('Resolving path.')
        if endpoint_path == '' or endpoint_path[0] != '/':
            logger.debug('Adding leading `/` to provided path')
            endpoint_path = '/' + endpoint_path
        try:
            resolved_route = resolve(endpoint_path)
            logger.debug('Resolved %s successfully', endpoint_path)
        except Resolver404:
            resolved_route = resolve(endpoint_path + '/')
            endpoint_path += '/'
            logger.warning('Endpoint path is missing a trailing slash: %s', endpoint_path)

        kwarg = resolved_route.kwargs
        for key, value in kwarg.items():
            # Replacing kwarg values back into the string seems to be the simplest way of bypassing complex regex
            # handling. However, its important not to freely use the .replace() function, as a {value} of `1` would
            # also cause the `1` in api/v1/ to be replaced
            var_index = endpoint_path.rfind(value)
            endpoint_path = endpoint_path[:var_index] + f'{{{key}}}' + endpoint_path[var_index + len(value) :]
        return endpoint_path, resolved_route

    except Resolver404:
        from django_swagger_tester.validation.utils import get_endpoint_paths

        logger.error(f'URL `%s` did not resolve successfully', endpoint_path)
        paths = get_endpoint_paths()
        closest_matches = ''.join([f'\n- {i}' for i in difflib.get_close_matches(endpoint_path, paths)])
        if closest_matches:
            raise ValueError(
                f'Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}\n\n'
                f'If your path contains path parameters (e.g., `/api/<version>/...`), make sure to pass a '
                f'value, and not the parameter pattern.'
            )
        raise ValueError(f'Could not resolve path `{endpoint_path}`')
