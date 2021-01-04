from openapi_tester.loaders import StaticSchemaLoader
from tests import yml_split_path


def test_successful_parse_reference(monkeypatch) -> None:
    """
    Asserts that a schema section that contains reference is returned successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_split_path)

    item = base.get_response_schema_section(route='/api/v1/cars/correct', method='GET', status_code=200)
    assert item == {
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


def test_successful_parse_external_reference(monkeypatch) -> None:
    """
    Asserts that a schema section that contains external reference is returned successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_split_path)

    item = base.get_response_schema_section(route='/api/v1/trucks/correct', method='GET', status_code=200)
    assert item == {
        'title': 'Success',
        'type': 'array',
        'items': {
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
