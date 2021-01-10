from openapi_tester.exceptions import CaseError
from openapi_tester.utils import format_openapi_tester_case_error


def test_format_openapi_tester_case_error():
    assert (
        format_openapi_tester_case_error(CaseError(key='IP', case='camel case', origin='middleware'))
        == "The response key `IP` is not properly camel case. Expected value: \n\nIf this is intentional, you can skip case validation by adding `ignore_case=['IP']` to the `validate_response` function call, or by adding the key to the CASE_PASSLIST in the OPENAPI_TESTER settings"
    )
