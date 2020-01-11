from django.urls import path

from .views.cars import Cars

urlpatterns = [
    path('v1/cars/', Cars.as_view(), name='cars'),
]
