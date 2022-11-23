from openapi_tester import SchemaTester
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.response import Response
from tests.utils import TEST_ROOT

schema_tester = SchemaTester(schema_file_path=str(TEST_ROOT) + "/schemas/manual_reference_schema.yaml")

class BaseAPITestCase(APITestCase):
    """Base test class for api views including schema validation"""

    @staticmethod
    def assertResponse(response: Response, **kwargs) -> None:
        """helper to run validate_response and pass kwargs to it"""
        schema_tester.validate_response(response=response, **kwargs)

# @override_settings(USE_X_FORWARDED_HOST=True)
class TeamsAPITests(BaseAPITestCase):
    def test_schema_using_assert_response(self):
        response = self.client.post(
            reverse(
                "team-members-relation",
                kwargs={
                    "version": "v1",
                    "pk": 1,
                    "related_field": "members",
                },
            ),
            content_type="application/vnd.api+json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertResponse(response)