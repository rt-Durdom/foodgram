from django.db import models

from users.models import User


class Tags (models.Model):
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
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
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
        verbose_name='Время приготовления'
    )
    is_published = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-is_published',)

    def __str__(self):
        return self.name


class RecipeIngredients (models.Model):
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
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipes} {self.ingredients} {self.amount}'
