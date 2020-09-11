import logging

from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..swagger.auto_schemas import get_snake_cased_response

logger = logging.getLogger('django_swagger_tester')


class SnakeCasedResponse(APIView):
    renderer_classes = [JSONRenderer]

    @get_snake_cased_response()
    def get(self, request: Request, **kwargs) -> Response:
        return Response({'this_is_snake_case': 'test'}, 200)
