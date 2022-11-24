from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from test_project import views
from test_project.api.views.animals import Animals
from test_project.api.views.cars import BadCars, GoodCars
from test_project.api.views.exempt_endpoint import Exempt
from test_project.api.views.i18n import Languages
from test_project.api.views.items import Items
from test_project.api.views.names import EmptyNameViewSet, NamesRetrieveView, NameViewSet
from test_project.api.views.pets import PetOwnerRelationshipView
from test_project.api.views.products import Products
from test_project.api.views.snake_cased_response import SnakeCasedResponse
from test_project.api.views.trucks import BadTrucks, GoodTrucks
from test_project.api.views.vehicles import Vehicles

router = routers.SimpleRouter()
router.register(r"names", NameViewSet)

api_urlpatterns = [
    path("api/<str:version>/cars/correct", GoodCars.as_view()),
    path("api/<str:version>/cars/incorrect", BadCars.as_view()),
    path("api/<str:version>/trucks/correct", GoodTrucks.as_view()),
    path("api/<str:version>/trucks/incorrect", BadTrucks.as_view()),
    path("api/<str:version>/vehicles", Vehicles.as_view()),
    path("api/<str:version>/animals", Animals.as_view()),
    path("api/<str:version>/items", Items.as_view()),
    path("api/<str:version>/exempt-endpoint", Exempt.as_view()),
    path("api/<str:version>/<str:pk>/names", NamesRetrieveView.as_view()),
    path("api/<str:version>/empty-names", EmptyNameViewSet.as_view({"get": "list"})),
    path("api/<str:version>/categories/<int:category_pk>/subcategories/<int:subcategory_pk>/", Products.as_view()),
    path("api/<str:version>/snake-case/", SnakeCasedResponse.as_view()),
    # ^trailing slash is here on purpose
    path("api/<str:version>/router_generated/", include(router.urls)),
    re_path(
        r"api/pet/(?P<petId>\d+)/relationships/(?P<relatedField>[-\w]+)",
        PetOwnerRelationshipView.as_view(),
        name="pet-owner-relation",
    ),
]

internationalised_urlpatterns = i18n_patterns(
    path("api/<str:version>/i18n", Languages.as_view()),
)

swagger_info = openapi.Info(
    title="DRF_YASG test project",
    default_version="v1",
    description="drf_yasg implementation for OpenAPI spec generation.",
    contact=openapi.Contact(email=""),
)
schema_view = get_schema_view(
    swagger_info,
    patterns=api_urlpatterns + internationalised_urlpatterns,
    public=False,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", views.index),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
urlpatterns += api_urlpatterns + internationalised_urlpatterns
