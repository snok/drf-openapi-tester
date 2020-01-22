import json

import yaml
from requests.exceptions import ConnectionError
from rest_framework.test import APISimpleTestCase, APIClient

from openapi_tester.exceptions import ImproperlyConfigured


class SpecificationFetcher(APISimpleTestCase):
    client = APIClient()

    def _authenticate(self) -> None:
        """
        Get valid user and attach credentials to client
        """
        from django.contrib.auth.models import User

        user, _ = User.objects.update_or_create(username='test_user')
        self.client.force_authenticate(user=user)

    def fetch_specification(self, path: str, url: bool) -> dict:
        """
        Fetches the hosted OpenAPI specification using the DRF APIClient.

        :param path: The path to the specification, str
        :param url: Indicates whether the path is an url, bool
        :return: OpenAPI specification
        """
        if url:
            try:
                self._authenticate()
                response = self.client.get(path, format='json')
            except ConnectionError as e:
                raise ConnectionError(
                    '\n\nNot able to connect to the specified openapi url. '
                    f'Please make sure the specified path is correct.\n\nError: {e}'
                )
            if 400 <= response.status_code <= 600:
                raise ImproperlyConfigured(
                    '\n\nCould not fetch the OpenAPI specification. Please make sure your documentation is '
                    f'set to public and that the path specified is correct.\n\nAPI response code: {response.status_code}'
                )

            return response.json()

        else:
            try:
                with open(path, 'r') as f:
                    content = f.read()
            except Exception as e:
                raise ImproperlyConfigured(
                    f'\n\nCould not read the openapi specification. ' f'Please make sure the path setting is correct.\n\nError: {e}'
                )
            if '.json' in path:
                return json.loads(content)
            elif '.yaml' in path:
                return yaml.load(content, Loader=yaml.FullLoader)
            else:
                raise ImproperlyConfigured('The specified file path does not seem to point to a JSON or YAML file.')
