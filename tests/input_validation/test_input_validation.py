def test_input_validation(client):
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg.base import validate_input
    validate_input(serializer=VehicleSerializer, method='POST', endpoint_url='api/v1/vehicles')
