from prance import ResolvingParser


def get_spec(url: str = 'http://127.0.0.1:8080/swagger/?format=openapi') -> dict:
    """
    Returns an API spec via HTTP request.
    # TODO: Hopefully this is a temporary solution - otherwise, find out how to run a server during testing
    :param url:
    :return:
    """
    parser = ResolvingParser(url, backend='openapi-spec-validator')
    return parser.specification


# TODO: Maybe resolve path instead of asking for it as a string
# Here it would require the user to pass in /correct/ -- no one is going to pass the / correctly


def get_endpoint(spec: dict, path: str, method: str) -> dict:
    """
    Returns the part of the schema we want to test for any single test.

    :param spec: OpenAPI specification
    :return: dict
    """
    methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    if method.casefold() not in methods:
        raise ValueError(f'Invalid value for `method`. Needs to be one of: {", ".join([i.upper() for i in methods])}.')
    return spec['paths'][path.casefold()][method.casefold()]
