import difflib
import logging

from django.urls import Resolver404, resolve
from requests import Response
from rest_framework.serializers import Serializer

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.response_tester import SwaggerTester
from django_swagger_tester.utils import get_paths

logger = logging.getLogger('django_swagger_tester')


class SwaggerTestBase(SwaggerTester):
    """
    Swagger tester base class.

    There's a few things that we need to do regardless of what we want to test. For example, we need to:

    - Load the OpenAPI schema
    - Resolve the endpoint url passed to our test methods
    - Validate the passed method
    """

    def __init__(self):
        self.endpoint_path = None  # <-- path we can use to index schema
        self.resolved_route = None  # <-- route resolved by django (doesnt always match schema)
        self.passed_route = None  # <-- original input `endpoint_url` - useful for logging
        self.method = None
        super().__init__()

    def load_schema(self) -> None:
        """
        This method should do one thing: Load the OpenAPI schema section we're testing, and add it to the class context as `self.schema`.

        Note that the class context holds the following variables by the time this method is called:

            - resolved_url: django.urls.resolvers.ResolverMatch
            - self.data: dictionary
            - self.status_code: integer
            - self.method: uppercase string
        """
        pass

    # ^ Methods above this line *should* be extended. Methods below *can* be extended.

    def resolve_path(self, endpoint_path: str) -> None:
        """
        Resolves a Django path.
        """
        try:
            logger.debug('Resolving path.')
            if endpoint_path[0] != '/':
                logger.debug('Adding leading `/` to provided path')
                endpoint_path = '/' + endpoint_path
            try:
                self.resolved_route = '/' + resolve(endpoint_path).route.replace('$', '')
                self.passed_route = endpoint_path
                logger.debug('Resolved %s successfully', endpoint_path)
                logger.debug('Resolved route: %s', self.resolved_route)
            except Resolver404:
                self.resolved_route = '/' + resolve(endpoint_path + '/').route
                self.passed_route = endpoint_path
                logger.warning('Endpoint path is missing a trailing slash (`/`)', endpoint_path)
        except Resolver404:
            logger.error(f'URL `%s` did not resolve succesfully', endpoint_path)
            paths = get_paths()
            closest_matches = ''.join([f'\n- {i}' for i in difflib.get_close_matches(endpoint_path, paths)])
            if closest_matches:
                raise ValueError(f'Could not resolve path `{endpoint_path}`.\n\nDid you mean one of these?{closest_matches}\n\n'
                                 f'If your path contains path parameters (e.g., `/api/<version>/...`), make sure to pass a '
                                 f'value, and not the parameter pattern.')
            else:
                raise ValueError(f'Could not resolve path `{endpoint_path}`')

    def validate_method(self, method: str) -> None:
        """
        Validates the specified HTTP method.
        """
        methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
        if not isinstance(method, str) or method.lower() not in methods:
            logger.error('Method `%s` is invalid. Should be one of: %s.', method, ', '.join([i.upper() for i in methods]))
            raise ValueError(f'Method `{method}` is invalid. Should be one of: {", ".join([i.upper() for i in methods])}.')
        self.method = method.upper()

    def set_ignored_keys(self, **kwargs) -> None:
        """
        Lets users pass a list of string that will not be checked by case-check.

        For example, validate_response(..., ignore_case=["List", "OF", "improperly cased", "kEYS"]).
        """
        if 'ignore_case' in kwargs:
            self.ignored_keys = kwargs['ignore_case']
