import re

from django.core.exceptions import ValidationError


def validate_username_format(value):
    if value == "me":
        raise ValidationError(
            "Использовать имя 'me' в качестве username запрещено."
        )
    match = re.match(r"^[\w.@+-]+$", value)
    if match is None or match.group() != value:
        raise ValidationError(
            "Имя пользователя может содержать только буквы, "
            "цифры и символы @ . + - _"
        )
    return value


def validate_password(value):
    if len(value) < 8:
        raise ValidationError(
            "Пароль должен содержать минимум 8 символов.",
            code="password_too_short",
        )
    if not any(char.isdigit() for char in value):
        raise ValidationError(
            "Пароль должен содержать хотя бы одну цифру.",
            code="password_no_digit",
        )
    if not any(char.isupper() for char in value):
        raise ValidationError(
            "Пароль должен содержать хотя бы одну заглавную букву.",
            code="password_no_uppercase",
        )
    if not any(char.islower() for char in value):
        raise ValidationError(
            "Пароль должен содержать хотя бы одну прописную букву.",
            code="password_no_lowercase",
        )
