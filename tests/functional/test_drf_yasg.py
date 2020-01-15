def test_drf_yasg_dynamic_schema(client) -> None:
    """
    Fetches a response from the /cars/ endpoint, in our drf_yasg demo project.
    The response is verified to check that it matches the response.

    :param client: Django client
    :returns: None
    """
    response = client.get('/api/v1/cars/correct')
