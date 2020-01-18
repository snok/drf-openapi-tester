# # flake8: noqa
# import requests
#
#
# def fetch_drf_yasg():
#     requests.get('http://127.0.0.1:8080/swagger/?format=openapi')
#     example_spec = {
#         'swagger': '2.0',
#         'info': {
#             'title': 'DRF_YASG test project',
#             'description': 'drf_yasg implementation for OpenAPI spec generation.',
#             'contact': {'email': ''},
#             'version': 'v1',
#         },
#         'host': 'localhost:8080',
#         'schemes': ['http'],
#         'basePath': '/api/v1',
#         'consumes': ['application/json'],
#         'produces': ['application/json'],
#         'securityDefinitions': {'Basic': {'type': 'basic'}},
#         'security': [{'Basic': []}],
#         'paths': {
#             '/cars/': {
#                 'get': {
#                     'operationId': 'get_cars',
#                     'summary': 'Lists cars',
#                     'description': 'Lists all cars available in this test-project',
#                     'parameters': [],
#                     'responses': {
#                         '200': {
#                             'description': '',
#                             'schema': {
#                                 'title': 'Success',
#                                 'type': 'object',
#                                 'properties': {
#                                     'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
#                                     'color': {'description': 'The color of the car.', 'type': 'string',
#                                               'example': 'Yellow'},
#                                     'height': {'description': 'How tall the car is.', 'type': 'string',
#                                                'example': 'Medium height'},
#                                     'width': {'description': 'How wide the car is.', 'type': 'string',
#                                               'example': 'Very wide'},
#                                     'length': {'description': 'How long the car is.', 'type': 'string',
#                                                'example': '2 meters'},
#                                 },
#                             },
#                         },
#                         '400': {
#                             'description': '',
#                             'schema': {
#                                 'title': 'Error',
#                                 'type': 'object',
#                                 'properties': {
#                                     'error': {
#                                         'description': 'Generic Error response for all API endpoints',
#                                         'type': 'string',
#                                         'example': 'Bad input. Error: {e}.',
#                                     }
#                                 },
#                             },
#                         },
#                         '401': {
#                             'description': '',
#                             'schema': {
#                                 'title': 'Error',
#                                 'type': 'object',
#                                 'properties': {
#                                     'error': {
#                                         'description': 'Generic Error response for all API endpoints',
#                                         'type': 'string',
#                                         'example': 'Bad credentials. Error: {e}.',
#                                     }
#                                 },
#                             },
#                         },
#                         '500': {
#                             'description': '',
#                             'schema': {
#                                 'title': 'Error',
#                                 'type': 'object',
#                                 'properties': {
#                                     'error': {
#                                         'description': 'Generic Error response for all API endpoints',
#                                         'type': 'string',
#                                         'example': 'Unexpected error raised when ...',
#                                     }
#                                 },
#                             },
#                         },
#                     },
#                     'tags': ['cars'],
#                 },
#                 'post': {
#                     'operationId': 'cars_create',
#                     'description': '',
#                     'parameters': [],
#                     'responses': {'201': {'description': ''}},
#                     'tags': ['cars'],
#                 },
#                 'put': {
#                     'operationId': 'cars_update',
#                     'description': '',
#                     'parameters': [],
#                     'responses': {'200': {'description': ''}},
#                     'tags': ['cars'],
#                 },
#                 'delete': {
#                     'operationId': 'cars_delete',
#                     'description': '',
#                     'parameters': [],
#                     'responses': {'204': {'description': ''}},
#                     'tags': ['cars'],
#                 },
#                 'parameters': [],
#             }
#         },
#         'definitions': {},
#     }
#     return example_spec
