from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientViewSet, CustomUserViewSet

router = DefaultRouter()
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("users", CustomUserViewSet, basename="users")

auth_patterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("auth/", include("djoser.urls")),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("", include(router.urls)),
]
