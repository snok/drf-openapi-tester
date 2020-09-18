import pytest

from django_swagger_tester.utils import Route, resolve_path


def test_route_initialization():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.deparameterized_path == '/api/{version}/{vehicle_type}/correct'
    assert route.parameterized_path == route.deparameterized_path
    assert route.counter == 0
    assert route.parameters == ['{version}', '{vehicle_type}']
    assert route.resolved_path.kwargs == {'version': 'v1', 'vehicle_type': 'cars'}


def test_route_iteration():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.parameterized_path == '/api/{version}/{vehicle_type}/correct'
    assert route.get_path() == '/api/{version}/{vehicle_type}/correct'
    assert route.get_path() == '/api/v1/{vehicle_type}/correct'
    assert route.get_path() == '/api/v1/cars/correct'
    route.reset()
    assert route.parameterized_path == '/api/{version}/{vehicle_type}/correct'


def test_route_matches():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.route_matches('/api/v1/{vehicle_type}/correct') is True
    assert route.route_matches('/api/{version}/{vehicle_type}/correct') is True
    assert route.route_matches('/api/v1/cars/correct') is True


def test_route_iteration_index_error():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.parameterized_path == '/api/{version}/{vehicle_type}/correct'
    assert route.get_path() == '/api/{version}/{vehicle_type}/correct'
    assert route.get_path() == '/api/v1/{vehicle_type}/correct'
    assert route.get_path() == '/api/v1/cars/correct'
    with pytest.raises(IndexError, match='No more parameters to insert'):
        route.get_path()
