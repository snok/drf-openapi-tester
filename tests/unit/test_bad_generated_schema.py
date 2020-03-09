# import pytest
#
# from django_swagger_tester.dynamic.get_schema import fetch_generated_schema
#
#
# def test_bad_response_code(monkeypatch) -> None:
#     """
#     Asserts that the right error message is raised when a bad HTTP method is passed.
#     """
#     from drf_yasg.utils import swagger_auto_schema
#     from demo_project.api.swagger.responses import generic_error_response
#     from demo_project.api.swagger import auto_schemas
#
#     def bad_auto_schema():
#         return swagger_auto_schema(
#             operation_id='get_cars',
#             operation_summary='Lists cars',
#             operation_description='Lists all cars available in this test-project',
#             responses={
#                 '400': generic_error_response('Bad input. Error: {e}.'),
#                 '401': generic_error_response('Bad credentials. Error: {e}.'),
#                 '500': generic_error_response('Unexpected error raised when ...'),
#             },
#         )
#
#
#     with pytest.raises(KeyError,
#                        match='No schema found for response code 200. Documented responses include 400, 401, 500.'):
#         monkeypatch.setattr(auto_schemas, "get_cars_auto_schema", bad_auto_schema)
#         print(bad_auto_schema(), '\n')
#         print(fetch_generated_schema(url='/cars/correct/', method='GET'))
#     monkeypatch.undo()
