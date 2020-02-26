from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING


def generic_string_schema(example, description):
    return Schema(type=TYPE_STRING, example=example, description=description)


def generic_int_schema(example, description):
    return Schema(type=TYPE_INTEGER, example=example, description=description)
