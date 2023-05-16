from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleFilter(admin.SimpleListFilter):
    title = "Роль пользователя"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        return [
            ("is_staff", "Администратор"),
            ("is_superuser", "Суперпользователь"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "is_staff":
            return queryset.filter(is_staff=True)
        elif value == "is_superuser":
            return queryset.filter(is_superuser=True)
        else:
            return queryset


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "email", "username", "first_name", "last_name")
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = (RoleFilter,)
