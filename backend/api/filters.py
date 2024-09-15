from django_filters.rest_framework import FilterSet, filters

from recipes.models import RecipeIngredients, Ingredients, Recipes

class IngredientFilter(FilterSet):
    """Фильтрация ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith',)

    class Meta:
        model = Ingredients
        fields = ('name',)