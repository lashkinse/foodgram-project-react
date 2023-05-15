from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import OuterRef, Exists

from recipes.validators import validate_hex_color

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тега", max_length=200, unique=True
    )
    color = models.CharField(
        verbose_name="Цвет в HEX",
        max_length=7,
        validators=[validate_hex_color],
    )
    slug = models.SlugField(
        verbose_name="Уникальный слаг", max_length=200, unique=True
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "color"], name="unique_name_color"
            )
        ]

    def __str__(self):
        return (
            f"Тег: {self.name}, "
            f"Цвет в HEX: {self.color}, "
            f"Уникальный слаг: {self.slug}"
        )


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200)
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=200
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit",
            )
        ]

    def __str__(self):
        return (
            f"Ингредиент: {self.name}, "
            f"Единица измерения: {self.measurement_unit}"
        )


class RecipeQuerySet(models.QuerySet):
    def filter_by_tags(self, tags):
        if tags:
            return self.filter(tags__slug__in=tags).distinct()
        return self.none()

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef("pk")
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCard.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef("pk")
                )
            ),
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(verbose_name="Название", max_length=200)
    image = models.ImageField(verbose_name="Картинка")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(Tag, through="RecipeTag")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[MinValueValidator(1)],
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "author"], name="unique_name_author_recipe"
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipe_ingredients"
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_tags"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="recipe_tags"
    )

    class Meta:
        verbose_name = "Тег в рецепте"
        verbose_name_plural = "Теги в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"], name="unique_recipe_tag"
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, related_name="favorites", on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name="favorites", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Пользователь и избранные рецепты"
        verbose_name_plural = "Пользователи и избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_favorite_recipe"
            )
        ]


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User,
        related_name="shopping_card",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shopping_card",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Пользователь и список покупок"
        verbose_name_plural = "Пользователи и списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe"
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author"
            )
        ]
