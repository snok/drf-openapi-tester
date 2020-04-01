string_type = {'description': 'This is a string type', 'type': 'string', 'example': 'string'}
integer_type = {'description': 'This is an integer type', 'type': 'integer', 'example': 1}
number_type = {'description': 'This is a number type', 'type': 'number', 'example': 1.1}
bool_type = {'description': 'This is a boolean type', 'type': 'boolean', 'example': True}
object_type = {
    'title': 'object_type_title',
    'type': 'object',
    'properties': {
        'string': string_type,
        'integer': integer_type,
        'number': number_type,
        'bool': bool_type,
    }
}
list_type = {'title': 'list_type_title', 'type': 'array', 'items': object_type}

string_data = 'string'
integer_data = 2
number_data = 2.2
bool_data = True
object_data = {'string': string_data, 'integer': integer_data, 'number': number_data, 'bool': bool_data}
list_data = [object_data,]
