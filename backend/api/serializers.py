from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import Tag, Ingredient, Follow, Recipe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and obj.following.filter(user=request.user).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def validate(self, attrs):
        user = self.context.get("request").user
        author = self.context.get("author")
        if author == user:
            raise serializers.ValidationError(
                {"error": "Нельзя подписаться на себя"}, code=400
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {"error": "Вы уже подписаны на этого автора"}, code=400
            )
        return attrs

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context.get("request").user, author=obj.author
        ).exists()

    @staticmethod
    def get_recipes(attrs):
        all_recipes = Recipe.objects.filter(author=attrs.author)
        return SubscriptionRecipeSerializer(all_recipes, many=True).data

    @staticmethod
    def get_recipes_count(attrs):
        all_recipes = Recipe.objects.filter(author=attrs.author)
        return all_recipes.count()
