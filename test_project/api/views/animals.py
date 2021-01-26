from uuid import uuid4

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from test_project.api.swagger.auto_schemas import animals_auto_schema


class Animals(APIView):
    @animals_auto_schema()
    def get(self, request: Request, version: int) -> Response:
        animals = {
            "dog": "very cool",
            "monkey": "very cool",
            "bird": "mixed reviews",
            "spider": "not cool",
            "random_uuid": uuid4(),
        }
        return Response(animals, HTTP_200_OK)

    def delete(self, request: Request, version: int) -> Response:
        return Response(status=HTTP_204_NO_CONTENT)
