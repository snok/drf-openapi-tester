from django_swagger_tester.response_validation.drf_yasg import validate_response


def test_endpoints_dynamic_schema(client, caplog) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    response = client.get('/api/v1/trucks/correct/')
    validate_response(response=response, method='GET', endpoint_url='/api/v1/trucks/correct/', ignore_case=['name', 'width', 'height'])
    assert [i in [record.message for record in caplog.records] for i in [
        'Skipping case check for key `name`', 'Skipping case check for key `name`',
        'Skipping case check for key `height`', 'Skipping case check for key `height`',
        'Skipping case check for key `width`', 'Skipping case check for key `width`',
    ]]
