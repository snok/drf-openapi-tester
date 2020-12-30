from django.utils.translation import gettext as _

from demo.api.swagger.auto_schemas import languages_auto_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class Languages(APIView):
    @languages_auto_schema()
    def get(self, request: Request, version: int) -> Response:
        return Response(
            {'languages': [_('French'), _('Spanish'), _('Greek'), _('Italian'), _('Portuguese')]}, HTTP_200_OK
        )
