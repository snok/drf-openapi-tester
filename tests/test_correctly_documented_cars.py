from .utils import APITestBase
import openapi_tester


class TestCorrectlyDocumentedCars(APITestBase):
    path = 'asd'

    @openapi_tester.wrap(schema=path2, case='camel')
    def test_get_200(self):

        expected_response = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]
        response = self.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

        # Test Swagger documentation
        openapi_tester.test_response(response, 'GET', self.path + '/correct/')  # TODO
