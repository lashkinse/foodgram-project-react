from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username_length, validate_username_format


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="Электронная почта",
        unique=True,
        max_length=settings.EMAIL_MAX_LEN,
        error_messages={
            "unique": "Пользователь с таким адресом электронной почты "
            "уже существует"
        },
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        unique=True,
        max_length=settings.USERNAME_MAX_LEN,
        validators=[validate_username_length, validate_username_format],
        error_messages={
            "unique": "Пользователь с таким именем уже существует"
        },
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=settings.FIRSTNAME_MAX_LEN
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=settings.LASTNAME_MAX_LEN
    )
    password = models.CharField(
        verbose_name="Пароль", max_length=settings.PASSWORD_MAX_LEN
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_username_email"
            )
        ]
