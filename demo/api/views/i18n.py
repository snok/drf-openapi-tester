from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from demo.api.swagger.auto_schemas import languages_auto_schema
from django_swagger_tester.views import ResponseValidationView


class Languages(ResponseValidationView):

    @languages_auto_schema()
    def get(self, request: Request) -> Response:
        return Response({'languages': [
            'French', 'Spanish', 'Greek', 'Italian', 'Portugese'
        ]}, HTTP_200_OK)
