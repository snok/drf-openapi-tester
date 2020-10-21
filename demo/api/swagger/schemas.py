from drf_yasg.openapi import TYPE_INTEGER, TYPE_STRING, Schema


def generic_string_schema(example, description):
    return Schema(type=TYPE_STRING, example=example, description=description)


def generic_int_schema(example, description):
    return Schema(type=TYPE_INTEGER, example=example, description=description)
