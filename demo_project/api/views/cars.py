import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# from django_swagger_tester.testing import validate
from ..swagger.auto_schemas import get_cars_auto_schema, get_other_cars_auto_schema

logger = logging.getLogger('django_swagger_tester')


class GoodCars(APIView):
    @staticmethod
    # @validate(response=True)
    @get_cars_auto_schema()
    def get(request: Request, **kwargs) -> Response:
        cars = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ]
        return Response(cars, 200)

    @staticmethod
    def put(request: Request) -> Response:
        pass

    @staticmethod
    def post(request: Request) -> Response:
        pass

    @staticmethod
    def delete(request: Request) -> Response:
        pass


class BadCars(APIView):
    @staticmethod
    # @validate(response=True)
    @get_other_cars_auto_schema()
    def get(request: Request, **kwargs) -> Response:
        cars = [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height',},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ]
        return Response(cars, 200)

    @staticmethod
    def put(request: Request) -> Response:
        pass

    @staticmethod
    def post(request: Request) -> Response:
        pass

    @staticmethod
    def delete(request: Request) -> Response:
        pass
