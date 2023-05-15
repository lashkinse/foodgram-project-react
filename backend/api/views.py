from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import ListRetrieveModelMixin
from api.permissions import IsAuthenticated, IsAuthorOrReadOnly
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    CustomUserSerializer,
    SubscriptionSerializer,
    FavoriteSerializer,
    ShoppingCardSerializer,
    RecipeSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Follow,
    Favorite,
    ShoppingCard,
    Recipe,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "post", "delete"]

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = CustomUserSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=True, methods=["POST"], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        serializer = SubscriptionSerializer(
            data=request.data, context={"request": request, "user": author}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        follow = get_object_or_404(Follow, user=request.user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ListRetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListRetrieveModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        user_id = (
            self.request.user.id
            if self.request.user.is_authenticated
            else None
        )
        return Recipe.objects.annotate_user_data(user_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
    )
    def add_to_shopping_cart(self, request, **kwargs):
        recipe = self.get_object()
        context = {"request": request, "recipe": recipe}
        serializer = ShoppingCardSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, recipe=recipe)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

    @action(
        detail=True,
        methods=["DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
    )
    def remove_from_shopping_cart(self, request, **kwargs):
        recipe = self.get_object()
        user = request.user
        if not ShoppingCard.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"error": "У вас не было этого рецепта в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_card = get_object_or_404(
            ShoppingCard, user=user, recipe=recipe
        )
        shopping_card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def add_to_favorite(self, request, **kwargs):
        recipe = self.get_object()
        context = {"request": request, "recipe": recipe}
        serializer = FavoriteSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, recipe=recipe)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED
            )

    @action(
        detail=True,
        methods=["DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def remove_from_favorite(self, request, **kwargs):
        recipe = self.get_object()
        user = request.user
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"error": "У вас не было этого рецепта в списке избранных"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite_recipe = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def download_recipes(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        recipe_list = [recipe.name for recipe in queryset]
        recipe_text = "\n".join(recipe_list)
        response = HttpResponse(recipe_text, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="recipes.txt"'
        return response
