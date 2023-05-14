from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

auth_patterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("auth/", include("djoser.urls")),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("", include(router.urls)),
]
