# flake8: noqa: U100
from django.shortcuts import redirect
from rest_framework.request import Request


def index(request: Request) -> redirect:
    """
    Redirects traffic from / to /swagger.
    """
    return redirect('schema-swagger-ui')
