# # flake8: noqa
# from prance import ResolvingParser
#
#
# def swagger_tester(response: Response, response_schema: Schema, enforce_camel_case: bool = True) -> None:
#     """
#     Validates input, #todo fetches openapi spec, and calls the test-class.
#
#     :param response: Response object
#     :param swagger_schema: OpenAPI Schema
#     :param enforce_camel_case: Bool, default True
#     :return: None
#     :raises: ValidationError #TODO: verify
#     """
#     if not isinstance(response_schema, Schema):
#         raise ValueError(f'`swagger_schema` should be an OpenAPI Schema, not a {type(swagger_schema)}.')
#
#     if not isinstance(enforce_camel_case, bool):
#         raise ValueError(f'`check_camel_case` should be a boolean, not a {type(enforce_camel_case)}.')
#
#     from drf_yasg.generators import get_schema
#
#     schema = get_schema()
#     # test = OpenAPITester()
#     # test.swagger_documentation(response=response, swagger_schema=swagger_schema, enforce_camel_case=enforce_camel_case)
#
#
# def get_spec(url: str = 'http://127.0.0.1:8080/swagger/?format=openapi') -> dict:
#     """
#     Returns an API spec via HTTP request.
#     # TODO: Hopefully this is a temporary solution - otherwise, find out how to run a server during testing
#     :param url:
#     :return:
#     """
#     parser = ResolvingParser(url, backend='openapi-spec-validator')
#     return parser.specification
#
#
# # TODO: Maybe resolve path instead of asking for it as a string
# # Here it would require the user to pass in /correct/ -- no one is going to pass the / correctly
#
#
# def get_endpoint(spec: dict, path: str, method: str) -> dict:
#     """
#     Returns the part of the schema we want to test for any single test.
#
#     :param spec: OpenAPI specification
#     :return: dict
#     """
#     methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
#     if method.casefold() not in methods:
#         raise ValueError(f'Invalid value for `method`. Needs to be one of: {", ".join([i.upper() for i in methods])}.')
#     return spec['paths'][path.casefold()][method.casefold()]
