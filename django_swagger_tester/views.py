from typing import List

from django.http import HttpRequest

from rest_framework.response import Response
from rest_framework.views import APIView

from django_swagger_tester.configuration import settings
from django_swagger_tester.utils import copy_response
from django_swagger_tester.validation import safe_validate_response


class ResponseValidationView(APIView):
    ignored_status_codes: List[int] = []

    def finalize_response(self, request: HttpRequest, response: Response, *args, **kwargs) -> Response:
        """
        Overwrites APIView's finalize_response so it validates response objects before returning them.
        """
        response = super().finalize_response(request, response, *args, **kwargs)
        if settings.view_settings.response_validation.debug and response.status_code not in self.ignored_status_codes:
            response.render()
            copied_response = copy_response(response)
            safe_validate_response(
                response=copied_response,
                path=request.path,
                method=request.method,
                func_logger=settings.view_settings.response_validation.logger,
            )
        return response
