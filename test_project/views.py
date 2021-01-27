# flake8: noqa: U100
from typing import Union

from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework.request import Request


def index(request: Request) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
    """
    Redirects traffic from / to /swagger.
    """
    return redirect("schema-swagger-ui")
