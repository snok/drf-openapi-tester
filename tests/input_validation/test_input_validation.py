def test_valid_input_validation(client):
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg.base import validate_input
    validate_input(serializer=VehicleSerializer, method='POST', route='api/v1/vehicles', underscoreize=True)

def test_invalid_input_validation(client):
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg.base import validate_input
    validate_input(serializer=VehicleSerializer, method='POST', route='api/v1/vehicles', underscoreize=False)
