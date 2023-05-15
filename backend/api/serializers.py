from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (
    Tag,
    Ingredient,
    Follow,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCard,
)

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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method in ["POST", "DELETE"]:
            self.fields.pop("name")
            self.fields.pop("measurement_unit")


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, recipe):
        user = self.context["request"].user
        return (
            not user.is_anonymous
            and user.favorites.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context["request"].user
        return (
            not user.is_anonymous
            and user.shopping_card.filter(recipe=recipe).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "author",
            "name",
            "text",
            "image",
            "cooking_time",
        )
        read_only_fields = ("author",)

    def validate(self, attrs):
        ingredients = attrs.get("ingredients", [])
        ingredients_id = []
        if (
            self.instance is None
            and Recipe.objects.filter(name=attrs.get("name")).exists()
        ):
            raise serializers.ValidationError(
                {"name": "Название рецепта должно быть уникальным"}, code=400
            )
        if not attrs.get("cooking_time") > 0:
            raise serializers.ValidationError(
                {"cooking_time": "Время приготовления должно быть больше нуля"}
            )
        for elem in ingredients:
            current_id = elem.get("id")
            amount = elem.get("amount")
            if current_id not in ingredients_id:
                ingredients_id.append(current_id)
            else:
                raise serializers.ValidationError(
                    {"id": "Ингредиент должен быть уникальным"}
                )
            if not amount > 0:
                raise serializers.ValidationError(
                    {"amount": "Количество должно быть больше нуля"}
                )
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=ingredient.get("id"),
                    recipe=recipe,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients
            ]
        )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient=ingredient.get("id"),
                    recipe=instance,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients
            ]
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.ImageField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = ("id", "name", "cooking_time", "image")

    def validate(self, attrs):
        user = self.context["request"].user
        recipe = self.context["recipe"]
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"error": "Рецепт уже находится в избранном"}, code=400
            )
        return attrs


class ShoppingCardSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.ImageField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = ShoppingCard
        fields = ("id", "name", "cooking_time", "image")

    def validate(self, attrs):
        user = self.context["request"].user
        recipe = self.context["recipe"]
        if ShoppingCard.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"error": "Рецепт уже находится в списке покупок"}, code=400
            )
        return attrs
