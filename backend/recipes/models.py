from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User

MIN_COUNT = 1
MAX_COUNT = 32000


class Tags (models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredients (models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipes (models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_COUNT), MaxValueValidator(MAX_COUNT)]
    )
    is_published = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-is_published',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:recipes-detail', kwargs={"pk": self.pk})


class RecipeIngredients (models.Model):
    """Модель ингредиентов для рецепта."""

    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_COUNT), MaxValueValidator(MAX_COUNT)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('recipes',)
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.recipes} {self.ingredients} {self.amount}'


class ShoppingCart(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipes, verbose_name='Рецепт', on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'корзины покупок'
        default_related_name = 'shopping_cart'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        default_related_name = 'favorite'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'


class ShortLink(models.Model):
    """Модель короткой для ссылки."""

    origin_url = models.URLField(
        max_length=255,
        verbose_name='Оригинальная ссылка',
    )
    short_url = models.CharField(
        max_length=132, verbose_name='Короткая ссылка', unique=True
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        ordering = ('short_url',)

    def __str__(self):
        return self.short_url
