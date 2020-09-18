from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from demo.api.swagger.auto_schemas import animals_auto_schema
from django_swagger_tester.wrapper import validate_response


class Animals(APIView):
    @animals_auto_schema()
    @validate_response
    def get(self, request: Request, version: int) -> Response:
        animals = {
            'dog': 'very cool',
            'monkey': 'very cool',
            'bird': 'mixed reviews',
            'spider': 'not cool',
        }
        return Response(animals, HTTP_200_OK)
