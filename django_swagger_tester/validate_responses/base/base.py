import difflib
import logging

from django.urls import Resolver404, resolve
from requests import Response

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.utils import list_project_urls
from django_swagger_tester.validate_responses.base.swagger_tester import SwaggerTester

logger = logging.getLogger('django_swagger_tester')


class SwaggerTestBase(SwaggerTester):
    """
    Swagger tester base class.
    """

    def validation(self) -> None:
        """
        Holds validation and setup logic to run when Django starts.
        """
        pass

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

    def _unpack_response(self, response: Response) -> None:
        """
        Unpacks response as dict.
        """
        try:
            self.data = response.json()
            self.status_code = response.status_code
        except Exception as e:
            logger.exception('Unable to open response object')
            raise ValueError(f'Unable to unpack response object. Make sure you are passing response, and not response.json(). Error: {e}')

    def _resolve_path(self, endpoint_path: str) -> None:
        """
        Resolves a Django path.
        """
        try:
            logger.debug('Resolving path.')
            if endpoint_path[0] != '/' or endpoint_path[-1] != '/':
                endpoint_path = f'/{endpoint_path}/'.replace('//', '/')
            self.resolved_url = resolve(endpoint_path)
        except Resolver404:
            logger.error(f'URL `%s` did not resolve succesfully', endpoint_path)
            list_of_urls = list_project_urls()
            closest_matches = ''.join([f'\n- /{i}' for i in difflib.get_close_matches(endpoint_path, list_of_urls)])
            if closest_matches:
                raise ValueError(f'Could not resolve path `{endpoint_path}`.\n\nDid you mean to resolve one of these?{closest_matches}')
            else:
                raise ValueError(f'Could not resolve path `{endpoint_path}`')

    def _validate_method(self, method: str) -> None:
        """
        Validates the specified HTTP method.
        """
        methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
        if not isinstance(method, str) or method.lower() not in methods:
            logger.error('Method `%s` is invalid. Should be one of: %s.', method, ', '.join([i.upper() for i in methods]))
            raise ValueError(f'Method `{method}` is invalid. Should be one of: {", ".join([i.upper() for i in methods])}.')
        self.method = method.upper()

    def _validate_response(self, response: Response, method: str, endpoint_url: str) -> None:
        """
        This function verifies that an OpenAPI schema definition matches the an API response.
        It inspects the schema recursively, and verifies that the schema matches the structure of the response at every level.

        :param response: HTTP response
        :param method: HTTP method ('get', 'put', 'post', ...)
        :param endpoint_url: Relative path of the endpoint being tested
        :raises: django_swagger_tester.exceptions.SwaggerDocumentationError
        """
        self._unpack_response(response)
        self._resolve_path(endpoint_url)
        self._validate_method(method)
        self.load_schema()
        if not self.schema:
            raise SwaggerDocumentationError('The OpenAPI schema is undefined. Schema is not testable.')
        if self.schema['type'] == 'object':
            self._dict(schema=self.schema, data=self.data)
        elif self.schema['type'] == 'array':
            self._list(schema=self.schema, data=self.data)
        elif self.schema['type'] == 'string' or self.schema['type'] == 'boolean' or self.schema['type'] == 'integer':
            self._item(schema=self.schema, data=self.data)
        else:
            raise Exception(f'Unexpected error.\nSchema: {self.schema}\n Response: {self.data}')
