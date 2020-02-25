"""demo_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework.schemas import get_schema_view

from . import views

version = '1.0.0'

api_urlpatterns = [
    path(
        'api/v1/cars/correct/',
        get_schema_view(title='Lists cars', description='Lists all cars available in this test-project', version=version),
        name='correctly_documented_cars',
    ),
    path(
        'api/v1/cars/incorrect/',
        get_schema_view(title='Lists other cars', description='Lists all other cars available in this test-project', version=version),
        name='incorrectly_documented_cars',
    ),
    path(
        'api/v1/trucks/correct/',
        get_schema_view(title='Lists trucks', description='Lists all trucks available in this test-project', version=version,),
        name='correctly_documented_trucks',
    ),
    path(
        'api/v1/trucks/incorrect/',
        get_schema_view(title='Lists other trucks', description='Lists all other trucks available in this test-project', version=version),
        name='incorrectly_documented_trucks',
    ),
]

schema_view = get_schema_view(title='Dynamic DRF test project', url='http://localhost:8080', patterns=api_urlpatterns,)

urlpatterns = [
    path('', views.index),
]
