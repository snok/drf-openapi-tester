from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView


class Exempt(APIView):
    def get(self, request: Request, version: int) -> Response:
        return Response(status=HTTP_204_NO_CONTENT)
