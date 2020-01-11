from openapi_tester.openapi_tester import openapi_tester


@openapi_tester(type='dynamic')
def test_import():
    print('this is a test')
