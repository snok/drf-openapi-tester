from rest_framework.views import APIView

from demo_project.api.swagger.auto_schemas import post_vehicle_auto_schema, VehicleSerializer


class Vehicles(APIView):

    @post_vehicle_auto_schema()
    def post(self, request):
        serializer = VehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
