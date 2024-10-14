from django.db import models
from django.contrib.auth.models import AbstractUser
# from djoser.serializers import UserSerializer


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
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
        verbose_name='Имя пользователя',
        null=True,
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
        verbose_name='Аватар',
        upload_to='users/',
        default=None,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscriber(models.Model):
    """Класс подписок на авторов."""

    user = models.ForeignKey(
        User, verbose_name='Пользователь', related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, verbose_name='Автор', related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
