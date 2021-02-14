from openapi_tester import SchemaTester

tester = SchemaTester()
parameterized_path = "/api/{version}/cars/correct"
de_parameterized_path = "/api/v1/cars/correct"
method = "get"
status = "200"
example_schema_array = {"type": "array", "items": {"type": "string"}}
example_array = ["string"]
example_schema_integer = {"type": "integer", "minimum": 3, "maximum": 5}
example_integer = 3
example_schema_number = {"type": "number", "minimum": 3, "maximum": 5}
example_number = 3.2
example_schema_object = {"type": "object", "properties": {"value": {"type": "integer"}}, "required": ["value"]}
example_object = {"value": 1}
example_schema_string = {"type": "string", "minLength": 3, "maxLength": 5}
example_string = "str"
example_response_types = [example_array, example_integer, example_number, example_object, example_string]
example_schema_types = [
    example_schema_array,
    example_schema_integer,
    example_schema_number,
    example_schema_object,
    example_schema_string,
]
example_anyof_response = {
    "type": "object",
    "anyOf": [
        {"properties": {"oneKey": {"type": "string"}}},
        {"properties": {"anotherKey": {"type": "integer"}}},
    ],
}
docs_anyof_example = {
    "type": "object",
    "anyOf": [
        {
            "required": ["age"],
            "properties": {
                "age": {"type": "integer"},
                "nickname": {"type": "string"},
            },
        },
        {
            "required": ["pet_type"],
            "properties": {
                "pet_type": {"type": "string", "enum": ["Cat", "Dog"]},
                "hunts": {"type": "boolean"},
            },
        },
    ],
}
bad_test_data = [
    {
        "url": "/api/v1/cars/incorrect",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height"},
            {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
            {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
        ],
    },
    {
        "url": "/api/v1/trucks/incorrect",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height"},
            {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
            {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
        ],
    },
    {
        "url": "/api/v1/trucks/incorrect",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height"},
            {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
            {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
        ],
    },
]
