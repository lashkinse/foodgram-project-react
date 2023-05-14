import re

from django.conf import settings
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


def validate_username_length(value):
    max_length = settings.USERNAME_MAX_LEN
    if len(value) > max_length:
        raise ValidationError(
            f"Имя должно быть не более {max_length} символов."
        )
    return value
