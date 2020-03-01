from openapi_tester import validate_response
from tests.functional.utils import APITestBase


class TestCorrectlyDocumentedCars(APITestBase):
    def setUp(self) -> None:
        from django.contrib.auth.models import User

        user, _ = User.objects.update_or_create(username='test_user')
        self.client.force_authenticate(user=user)
        self.path = '/api/v1/cars'

    def test_get_200(self):
        expected_response = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]
        response = self.get('correctly_documented_cars')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        # Test Swagger documentation
        validate_response(response.json(), 'GET', self.path + '/correct/')


class TestCorrectlyDocumentedTrucks(APITestBase):
    def setUp(self) -> None:
        from django.contrib.auth.models import User

        user, _ = User.objects.update_or_create(username='test_user')
        self.client.force_authenticate(user=user)
        self.path = '/api/v1/trucks'

    def test_get_200(self):
        expected_response = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]
        response = self.get('correctly_documented_trucks')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        # Test Swagger documentation
        validate_response(response.json(), 'GET', self.path + '/correct/')
