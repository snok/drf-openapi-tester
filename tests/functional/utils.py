from django.contrib.auth.models import User
from django.urls import reverse
from requests.models import Response
from rest_framework.test import APITestCase


class APITestBase(APITestCase):
    def _authenticate(self) -> None:
        """
        Get valid user and attach credentials to client
        """
        user, _ = User.objects.update_or_create(username='testuser')
        self.client.force_authenticate(user=user)

    def get(self, path: str, params: str = None) -> Response:
        """
        GETs an endpoint.
        :param path: path of the endpoint
        :param params: optional path parameters
        :return: response
        """
        if params is None:
            url = reverse(f'{path}')
        else:
            url = reverse(f'{path}') + params
        self._authenticate()
        response = self.client.get(url, headers={'Content-Type': 'application/json'})
        return response
