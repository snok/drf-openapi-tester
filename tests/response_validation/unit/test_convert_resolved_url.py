from django_swagger_tester.utils import convert_resolved_route


def test_convert_url():
    """
    Verifies that conversion works
    """
    assert (
        convert_resolved_route('/api/<version:version>/<something:something>/<somethingsomething:somethingsomething>/')
        == '/api/{version}/{something}/{somethingsomething}/'
    )
    assert (
        convert_resolved_route('/api/<version>/<something>/<somethingsomething>/')
        == '/api/{version}/{something}/{somethingsomething}/'
    )
