from django.contrib.auth.models import User
from requests.models import Response
from rest_framework.test import APITestCase

from response_tester.testing import validate_response


class APITestBase(APITestCase):
    def _authenticate(self) -> None:
        """
        Get valid user and attach credentials to client
        """
        user, _ = User.objects.update_or_create(username="testuser")
        self.client.force_authenticate(user=user)

    def get(self, path: str, params: str = None) -> Response:
        """
        GETs an endpoint.
        :param path: path of the endpoint
        :param params: optional path parameters
        :return: response
        """
        self._authenticate()
        return self.client.get(path, headers={"Content-Type": "application/json"})


class TestCorrectlyDocumentedCars(APITestBase):
    def setUp(self) -> None:
        user, _ = User.objects.update_or_create(username="test_user")
        self.client.force_authenticate(user=user)
        self.path = "/api/v1/cars"

    def test_get_200(self):
        expected_response = [
            {"name": "Saab", "color": "Yellow", "height": "Medium height", "width": "Very wide", "length": "2 meters"},
            {"name": "Volvo", "color": "Red", "height": "Medium height", "width": "Not wide", "length": "2 meters"},
            {"name": "Tesla", "color": "black", "height": "Medium height", "width": "Wide", "length": "2 meters"},
        ]
        response = self.get(self.path + "/correct/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        # Test Swagger documentation
        validate_response(response=response, method="GET", route=self.path + "/correct/")


class TestCorrectlyDocumentedTrucks(APITestBase):
    def setUp(self) -> None:
        from django.contrib.auth.models import User

        user, _ = User.objects.update_or_create(username="test_user")
        self.client.force_authenticate(user=user)
        self.path = "/api/v1/trucks"

    def test_get_200(self):
        expected_response = [
            {"name": "Saab", "color": "Yellow", "height": "Medium height", "width": "Very wide", "length": "2 meters"},
            {"name": "Volvo", "color": "Red", "height": "Medium height", "width": "Not wide", "length": "2 meters"},
            {"name": "Tesla", "color": "black", "height": "Medium height", "width": "Wide", "length": "2 meters"},
        ]
        response = self.get(self.path + "/correct/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        # Test Swagger documentation
        validate_response(response=response, method="GET", route=self.path + "/correct/")
