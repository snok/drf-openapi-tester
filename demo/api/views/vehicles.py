from demo.api.swagger.auto_schemas import VehicleSerializer, post_vehicle_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView


class Vehicles(APIView):
    @post_vehicle_auto_schema()
    def post(self, request, version: int):
        serializer = VehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': 'this is a response'}, 201)
