from django_swagger_tester.response_validation.drf_yasg import validate_response


def test_endpoints_dynamic_schema(client, caplog) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    response = client.get('/api/v1/trucks/correct/')
    validate_response(response=response, method='GET', endpoint_url='/api/v1/trucks/correct/', ignore_case=['name', 'width', 'height'])
    assert [i.message for i in caplog.records] == [
        'Returning `camel case` case function', 'Resolving path.',
        'Resolved /api/v1/trucks/correct/ successfully', 'Fetching generated dynamic schema',
        'Verifying that response list layer matches schema layer', 'Calling _dict from _list',
        'Verifying that response dict layer matches schema layer',
        'Skipping case check for key `name`', 'Skipping case check for key `name`',
        "Calling _item from _dict. Response: Saab, Schema: {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'}",
        'Verifying that `color` is properly camel cased',
        'Verifying that `color` is properly camel cased',
        "Calling _item from _dict. Response: Yellow, Schema: {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'}",
        'Skipping case check for key `height`', 'Skipping case check for key `height`',
        "Calling _item from _dict. Response: Medium height, Schema: {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'}",
        'Skipping case check for key `width`', 'Skipping case check for key `width`',
        "Calling _item from _dict. Response: Very wide, Schema: {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'}",
        'Verifying that `length` is properly camel cased',
        'Verifying that `length` is properly camel cased',
        "Calling _item from _dict. Response: 2 meters, Schema: {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'}",
        'Calling _dict from _list', 'Verifying that response dict layer matches schema layer',
        'Skipping case check for key `name`', 'Skipping case check for key `name`',
        "Calling _item from _dict. Response: Volvo, Schema: {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'}",
        'Verifying that `color` is properly camel cased',
        'Verifying that `color` is properly camel cased',
        "Calling _item from _dict. Response: Red, Schema: {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'}",
        'Skipping case check for key `height`', 'Skipping case check for key `height`',
        "Calling _item from _dict. Response: Medium height, Schema: {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'}",
        'Skipping case check for key `width`', 'Skipping case check for key `width`',
        "Calling _item from _dict. Response: Not wide, Schema: {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'}",
        'Verifying that `length` is properly camel cased',
        'Verifying that `length` is properly camel cased',
        "Calling _item from _dict. Response: 2 meters, Schema: {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'}",
        'Calling _dict from _list', 'Verifying that response dict layer matches schema layer',
        'Skipping case check for key `name`', 'Skipping case check for key `name`',
        "Calling _item from _dict. Response: Tesla, Schema: {'description': 'A swedish truck?', 'type': 'string', 'example': 'Saab'}",
        'Verifying that `color` is properly camel cased',
        'Verifying that `color` is properly camel cased',
        "Calling _item from _dict. Response: black, Schema: {'description': 'The color of the truck.', 'type': 'string', 'example': 'Yellow'}",
        'Skipping case check for key `height`', 'Skipping case check for key `height`',
        "Calling _item from _dict. Response: Medium height, Schema: {'description': 'How tall the truck is.', 'type': 'string', 'example': 'Medium height'}",
        'Skipping case check for key `width`', 'Skipping case check for key `width`',
        "Calling _item from _dict. Response: Wide, Schema: {'description': 'How wide the truck is.', 'type': 'string', 'example': 'Very wide'}",
        'Verifying that `length` is properly camel cased',
        'Verifying that `length` is properly camel cased',
        "Calling _item from _dict. Response: 2 meters, Schema: {'description': 'How long the truck is.', 'type': 'string', 'example': '2 meters'}"
    ]
