from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует',
        },
        verbose_name='Электронная почта'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким username уже существует',
        },
        verbose_name='Имя пользователя'
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    avatar = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username 
