import pytest

from openapi_tester.utils import parse_endpoint

schema = {
    'swagger': '2.0',
    'info': {
        'title': 'DRF_YASG test project',
        'description': 'drf_yasg implementation for OpenAPI spec generation.',
        'contact': {'email': ''},
        'version': 'v1',
    },
    'host': 'localhost:8080',
    'schemes': ['http'],
    'basePath': '/api/v1',
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'securityDefinitions': {'Basic': {'type': 'basic'}},
    'security': [{'Basic': []}],
    'paths': {
        '/cars/correct/': {
            'get': {
                'operationId': 'get_cars',
                'summary': 'Lists cars',
                'description': 'Lists all cars available in this test-project',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': '',
                        'schema': {
                            'title': 'Success',
                            'type': 'array',
                            'items': {
                                'title': 'Success',
                                'type': 'object',
                                'properties': {
                                    'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
                                    'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
                                    'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
                                    'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
                                    'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
                                },
                            },
                        },
                    },
                    '400': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad input. Error: {e}.',
                                }
                            },
                        },
                    },
                    '401': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad credentials. Error: {e}.',
                                }
                            },
                        },
                    },
                    '500': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Unexpected error raised when ...',
                                }
                            },
                        },
                    },
                },
                'tags': ['cars'],
            },
            'post': {
                'operationId': 'cars_correct_create',
                'description': '',
                'parameters': [],
                'responses': {'201': {'description': ''}},
                'tags': ['cars'],
            },
            'put': {
                'operationId': 'cars_correct_update',
                'description': '',
                'parameters': [],
                'responses': {'200': {'description': ''}},
                'tags': ['cars'],
            },
            'delete': {
                'operationId': 'cars_correct_delete',
                'description': '',
                'parameters': [],
                'responses': {'204': {'description': ''}},
                'tags': ['cars'],
            },
            'parameters': [],
        },
        '/cars/incorrect/': {
            'get': {
                'operationId': 'get_other_cars',
                'summary': 'Lists other cars',
                'description': 'Lists all other cars available in this test-project',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': '',
                        'schema': {
                            'title': 'Success',
                            'type': 'array',
                            'items': {
                                'title': 'Success',
                                'type': 'object',
                                'properties': {
                                    'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
                                    'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
                                    'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
                                    'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
                                    'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
                                },
                            },
                        },
                    },
                    '400': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad input. Error: {e}.',
                                }
                            },
                        },
                    },
                    '401': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad credentials. Error: {e}.',
                                }
                            },
                        },
                    },
                    '500': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Unexpected error raised when ...',
                                }
                            },
                        },
                    },
                },
                'tags': ['cars'],
            },
            'post': {
                'operationId': 'cars_incorrect_create',
                'description': '',
                'parameters': [],
                'responses': {'201': {'description': ''}},
                'tags': ['cars'],
            },
            'put': {
                'operationId': 'cars_incorrect_update',
                'description': '',
                'parameters': [],
                'responses': {'200': {'description': ''}},
                'tags': ['cars'],
            },
            'delete': {
                'operationId': 'cars_incorrect_delete',
                'description': '',
                'parameters': [],
                'responses': {'204': {'description': ''}},
                'tags': ['cars'],
            },
            'parameters': [],
        },
        '/trucks/correct/': {
            'get': {
                'operationId': 'get_trucks',
                'summary': 'Lists trucks',
                'description': 'Lists all trucks available in this test-project',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': '',
                        'schema': {
                            'title': 'Success',
                            'type': 'array',
                            'items': {
                                'title': 'Success',
                                'type': 'object',
                                'properties': {
                                    'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                                    'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                                    'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                                    'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                                    'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
                                },
                            },
                        },
                    },
                    '400': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad input. Error: {e}.',
                                }
                            },
                        },
                    },
                    '401': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad credentials. Error: {e}.',
                                }
                            },
                        },
                    },
                    '500': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Unexpected error raised when ...',
                                }
                            },
                        },
                    },
                },
                'tags': ['trucks'],
            },
            'post': {
                'operationId': 'trucks_correct_create',
                'description': '',
                'parameters': [],
                'responses': {'201': {'description': ''}},
                'tags': ['trucks'],
            },
            'put': {
                'operationId': 'trucks_correct_update',
                'description': '',
                'parameters': [],
                'responses': {'200': {'description': ''}},
                'tags': ['trucks'],
            },
            'delete': {
                'operationId': 'trucks_correct_delete',
                'description': '',
                'parameters': [],
                'responses': {'204': {'description': ''}},
                'tags': ['trucks'],
            },
            'parameters': [],
        },
        '/trucks/incorrect/': {
            'get': {
                'operationId': 'get_other_trucks',
                'summary': 'Lists other trucks',
                'description': 'Lists all other trucks available in this test-project',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': '',
                        'schema': {
                            'title': 'Success',
                            'type': 'array',
                            'items': {
                                'title': 'Success',
                                'type': 'object',
                                'properties': {
                                    'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                                    'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                                    'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                                    'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                                    'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
                                },
                            },
                        },
                    },
                    '400': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad input. Error: {e}.',
                                }
                            },
                        },
                    },
                    '401': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad credentials. Error: {e}.',
                                }
                            },
                        },
                    },
                    '500': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Unexpected error raised when ...',
                                }
                            },
                        },
                    },
                },
                'tags': ['trucks'],
            },
            'post': {
                'operationId': 'trucks_incorrect_create',
                'description': '',
                'parameters': [],
                'responses': {'201': {'description': ''}},
                'tags': ['trucks'],
            },
            'put': {
                'operationId': 'trucks_incorrect_update',
                'description': '',
                'parameters': [],
                'responses': {'200': {'description': ''}},
                'tags': ['trucks'],
            },
            'delete': {
                'operationId': 'trucks_incorrect_delete',
                'description': '',
                'parameters': [],
                'responses': {'204': {'description': ''}},
                'tags': ['trucks'],
            },
            'parameters': [],
        },
    },
    'definitions': {},
}


def test_valid_parse():
    sub_dict = parse_endpoint(schema, 'get', '/api/v1/cars/correct/')
    assert sub_dict == {
        'title': 'Success',
        'type': 'array',
        'items': {
            'title': 'Success',
            'type': 'object',
            'properties': {
                'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
                'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
                'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
                'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
                'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
            },
        },
    }
    sub_dict = parse_endpoint(schema, 'get', '/api/v1/cars/incorrect/')
    assert sub_dict == {
        'title': 'Success',
        'type': 'array',
        'items': {
            'title': 'Success',
            'type': 'object',
            'properties': {
                'name': {'description': 'A swedish car?', 'type': 'string', 'example': 'Saab'},
                'color': {'description': 'The color of the car.', 'type': 'string', 'example': 'Yellow'},
                'height': {'description': 'How tall the car is.', 'type': 'string', 'example': 'Medium height'},
                'width': {'description': 'How wide the car is.', 'type': 'string', 'example': 'Very wide'},
                'length': {'description': 'How long the car is.', 'type': 'string', 'example': '2 meters'},
            },
        },
    }
    sub_dict = parse_endpoint(schema, 'get', '/api/v1/trucks/correct/')
    assert sub_dict == {
        'title': 'Success',
        'type': 'array',
        'items': {
            'title': 'Success',
            'type': 'object',
            'properties': {
                'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
            },
        },
    }
    sub_dict = parse_endpoint(schema, 'get', '/api/v1/trucks/incorrect/')
    assert sub_dict == {
        'title': 'Success',
        'type': 'array',
        'items': {
            'title': 'Success',
            'type': 'object',
            'properties': {
                'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
            },
        },
    }


def test_invalid_method():
    for method in ['patch', 'options', 'head']:
        with pytest.raises(KeyError, match=f'The OpenAPI schema has no method called `{method}`'):
            parse_endpoint(schema, method, '/api/v1/cars/correct/')

    for method in ['test', '', None]:
        with pytest.raises(
            ValueError, match='Invalid value for `method`. Needs to be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.'
        ):
            parse_endpoint(schema, method, '/api/v1/cars/correct/')


def test_invalid_paths():
    for bad_path in ['', 'api', 'correct']:
        with pytest.raises(ValueError, match=f'Could not resolve path `{bad_path}'):
            parse_endpoint(schema, 'get', bad_path)


schema_missing_an_endpoint = {
    'swagger': '2.0',
    'info': {
        'title': 'DRF_YASG test project',
        'description': 'drf_yasg implementation for OpenAPI spec generation.',
        'contact': {'email': ''},
        'version': 'v1',
    },
    'host': 'localhost:8080',
    'schemes': ['http'],
    'basePath': '/api/v1',
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'securityDefinitions': {'Basic': {'type': 'basic'}},
    'security': [{'Basic': []}],
    'paths': {
        '/trucks/incorrect/': {
            'get': {
                'operationId': 'get_other_trucks',
                'summary': 'Lists other trucks',
                'description': 'Lists all other trucks available in this test-project',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': '',
                        'schema': {
                            'title': 'Success',
                            'type': 'array',
                            'items': {
                                'title': 'Success',
                                'type': 'object',
                                'properties': {
                                    'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                                    'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                                    'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                                    'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                                    'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
                                },
                            },
                        },
                    },
                    '400': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad input. Error: {e}.',
                                }
                            },
                        },
                    },
                    '401': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad credentials. Error: {e}.',
                                }
                            },
                        },
                    },
                    '500': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Unexpected error raised when ...',
                                }
                            },
                        },
                    },
                },
                'tags': ['trucks'],
            },
            'post': {
                'operationId': 'trucks_incorrect_create',
                'description': '',
                'parameters': [],
                'responses': {'201': {'description': ''}},
                'tags': ['trucks'],
            },
            'put': {
                'operationId': 'trucks_incorrect_update',
                'description': '',
                'parameters': [],
                'responses': {'200': {'description': ''}},
                'tags': ['trucks'],
            },
            'delete': {
                'operationId': 'trucks_incorrect_delete',
                'description': '',
                'parameters': [],
                'responses': {'204': {'description': ''}},
                'tags': ['trucks'],
            },
            'parameters': [],
        },
        '/incorrect/': {
            'get': {
                'operationId': 'get_other_trucks',
                'summary': 'Lists other trucks',
                'description': 'Lists all other trucks available in this test-project',
                'parameters': [],
                'responses': {
                    '200': {
                        'description': '',
                        'schema': {
                            'title': 'Success',
                            'type': 'array',
                            'items': {
                                'title': 'Success',
                                'type': 'object',
                                'properties': {
                                    'name': {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'},
                                    'color': {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'},
                                    'height': {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'},
                                    'width': {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'},
                                    'length': {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'},
                                },
                            },
                        },
                    },
                    '400': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad input. Error: {e}.',
                                }
                            },
                        },
                    },
                    '401': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Bad credentials. Error: {e}.',
                                }
                            },
                        },
                    },
                    '500': {
                        'description': '',
                        'schema': {
                            'title': 'Error',
                            'type': 'object',
                            'properties': {
                                'error': {
                                    'description': 'Generic Error response for all API endpoints',
                                    'type': 'string',
                                    'example': 'Unexpected error raised when ...',
                                }
                            },
                        },
                    },
                },
                'tags': ['trucks'],
            },
            'post': {
                'operationId': 'trucks_incorrect_create',
                'description': '',
                'parameters': [],
                'responses': {'201': {'description': ''}},
                'tags': ['trucks'],
            },
            'put': {
                'operationId': 'trucks_incorrect_update',
                'description': '',
                'parameters': [],
                'responses': {'200': {'description': ''}},
                'tags': ['trucks'],
            },
            'delete': {
                'operationId': 'trucks_incorrect_delete',
                'description': '',
                'parameters': [],
                'responses': {'204': {'description': ''}},
                'tags': ['trucks'],
            },
            'parameters': [],
        },
    },
    'definitions': {},
}


def test_query_bad_schema():
    with pytest.raises(ValueError, match='Could not match the resolved url to a documented endpoint in the OpenAPI specification'):
        sub_dict = parse_endpoint(schema_missing_an_endpoint, 'get', '/api/v1/cars/correct/')


def test_multiple_matches():
    with pytest.raises(ValueError, match='Matched the resolved urls to too many endpoints'):
        sub_dict = parse_endpoint(schema_missing_an_endpoint, 'get', '/api/v1/trucks/incorrect/')
