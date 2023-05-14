from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, IngredientViewSet, CustomUserViewSet

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")

auth_patterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("", include(router.urls)),
]
