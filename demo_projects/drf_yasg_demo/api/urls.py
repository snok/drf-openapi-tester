from django.urls import path

from .views.cars import GoodCars, BadCars

urlpatterns = [
    path('v1/cars/correct/', GoodCars.as_view(), name='correctly_documented_cars'),
    path('v1/cars/incorrect/', BadCars.as_view(), name='incorrectly_documented_cars'),
]
