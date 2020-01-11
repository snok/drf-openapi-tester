from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..swagger.auto_schemas import get_cars_auto_schema


class Cars(APIView):
    @staticmethod
    @get_cars_auto_schema()
    def get(request: Request) -> Response:
        return Response({'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}, 200)

    @staticmethod
    def put(request: Request) -> Response:
        pass

    @staticmethod
    def post(request: Request) -> Response:
        pass

    @staticmethod
    def delete(request: Request) -> Response:
        pass
