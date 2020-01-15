from rest_framework.test import APITestCase
from .api.swagger.responses import get_cars_200_response
from openapi_tester.openapi_tester import openapi_tester


class TestEndpoints(APITestCase):
    @openapi_tester('dynamic')
    def test_correctly_documented_endpoint(self):
        """
        # TODO: document

        :return:
        """
        response = self.client.get('/api/v1/cars/correct/', format='json')
        self.assertCorrectSchema(response=response, response_schema=get_cars_200_response())
