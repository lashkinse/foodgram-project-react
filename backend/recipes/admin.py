from django.contrib import admin
from django.db.models import Count

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCard,
    Tag,
)


class RecipeIngredientLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientLine]
    list_display = ("pk", "name", "author", "favorites_count")
    list_filter = ("name", "author", "tags")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(favorites_count=Count("favorite"))
        )

    def favorites_count(self, obj):
        return obj.favorites_count

    favorites_count.short_description = "Добавлений в избранное"
    favorites_count.admin_order_field = "favorites_count"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


admin.site.register(Tag)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Follow)
admin.site.register(ShoppingCard)
admin.site.register(Favorite)
