import re

from django.core.exceptions import ValidationError


def validate_hex_color(value):
    hex_regex = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if not re.match(hex_regex, value):
        raise ValidationError("Неверный формат цвета")
