from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import CarSerializer
from ..swagger.auto_schemas import get_cars_auto_schema, get_other_cars_auto_schema


class GoodCars(APIView):
    @staticmethod
    @extend_schema(
        responses={200: CarSerializer(many=True)}
    )
    @get_cars_auto_schema()
    def get(request: Request, version: int, **kwargs) -> Response:
        cars = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]
        return Response(cars, 200)

    @staticmethod
    def put(request: Request, version: int, vehicle_type: str) -> Response:
        return Response({})

    @staticmethod
    def post(request: Request, version: int, vehicle_type: str) -> Response:
        return Response({})

    @staticmethod
    def delete(request: Request, version: int, vehicle_type: str) -> Response:
        return Response({})


class BadCars(APIView):
    @staticmethod
    @get_other_cars_auto_schema()
    def get(request: Request, version: int, **kwargs) -> Response:
        cars = [
            {
                'name': 'Saab',
                'color': 'Yellow',
                'height': 'Medium height',
            },
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ]
        return Response(cars, 200)

    @staticmethod
    def put(request: Request, version: int, vehicle_type: str) -> Response:
        return Response({})

    @staticmethod
    def post(request: Request, version: int, vehicle_type: str) -> Response:
        return Response({})

    @staticmethod
    def delete(request: Request, version: int, vehicle_type: str) -> Response:
        return Response({})
