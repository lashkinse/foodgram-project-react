from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    IngredientViewSet,
    CustomUserViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")

auth_patterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]

urlpatterns = [
    path("", include(auth_patterns)),
    path("", include(router.urls)),
]
