from unittest.mock import patch

from rest_framework.test import APITestCase

from openapi_tester.schema_tester import SchemaTester
from tests.test_schema_tester import test_reference_schema
from tests.utils import CURRENT_PATH

schema_path = str(CURRENT_PATH) + '/schemas/openapi_v3_reference_schema.yaml'
tester = SchemaTester(schema_file_path='')

OpenAPISchemaTesterTestCase = tester.test_case()


def test_subclass():
    assert issubclass(OpenAPISchemaTesterTestCase, APITestCase)


class TestTestCase(OpenAPISchemaTesterTestCase):

    # TODO: Find a way to hook onto existing tests, and just patching out the method called

    def test_schema_validation(self):
        with patch(
            'tests.test_schema_tester.SchemaTester.validate_response', OpenAPISchemaTesterTestCase.assertResponse
        ):
            test_reference_schema()
