from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.validators import (validate_username_length,
                              validate_username_format)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей"""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )

    @staticmethod
    def validate_username(value):
        validators = [
            validate_username_length,
            validate_username_format,
        ]
        for validator in validators:
            validator(value)
        return value
