from tests.utils import yml_split_path

from django_swagger_tester.loaders import StaticSchemaLoader


def test_successful_parse_reference(monkeypatch) -> None:
    """
    Asserts that a schema section that contains reference is returned successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_split_path)

    item = base.get_response_schema_section(route="/api/v1/cars/correct", method="GET", status_code=200)
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
