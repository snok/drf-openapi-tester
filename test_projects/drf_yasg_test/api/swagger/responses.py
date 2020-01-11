from drf_yasg.openapi import Schema, TYPE_OBJECT

from .schemas import generic_string_schema


def generic_error_response(error_description) -> Schema:
    return Schema(
        title='Error',
        type=TYPE_OBJECT,
        properties={'error': generic_string_schema(error_description, 'Generic Error response for all API endpoints')},
    )


def get_cars_200_response() -> Schema:
    return Schema(
        title='Success',
        type=TYPE_OBJECT,
        properties={
            'name': generic_string_schema(example='Saab', description='A swedish car?'),
            'color': generic_string_schema(example='Yellow', description='The color of the car.'),
            'height': generic_string_schema(example='Medium height', description='How tall the car is.'),
            'width': generic_string_schema(example='Very wide', description='How wide the car is.'),
            'length': generic_string_schema(example='2 meters', description='How long the car is.'),
        },
    )
