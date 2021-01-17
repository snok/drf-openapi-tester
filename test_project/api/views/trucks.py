from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import CarSerializer
from ..swagger.auto_schemas import get_other_trucks_auto_schema, get_trucks_auto_schema


class GoodTrucks(APIView):
    @staticmethod
    @extend_schema(responses={200: CarSerializer(many=True)})
    @get_trucks_auto_schema()
    def get(request: Request, version: int) -> Response:
        trucks = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]
        return Response(trucks, 200)

    @staticmethod
    def put(request: Request) -> Response:
        pass

    @staticmethod
    def post(request: Request) -> Response:
        pass

    @staticmethod
    def delete(request: Request) -> Response:
        pass


class BadTrucks(APIView):
    @staticmethod
    @extend_schema(responses={200: CarSerializer(many=True)})
    @get_other_trucks_auto_schema()
    def get(request: Request, version: int) -> Response:
        trucks = [
            {
                'name': 'Saab',
                'color': 'Yellow',
                'height': 'Medium height',
            },
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ]
        return Response(trucks, 200)

    @staticmethod
    def put(request: Request, version: int) -> Response:
        pass

    @staticmethod
    def post(request: Request, version: int) -> Response:
        pass

    @staticmethod
    def delete(request: Request, version: int) -> Response:
        pass
