from django_filters.rest_framework import FilterSet, filters

from recipes.models import Tags, Ingredients, Recipes

class IngredientFilter(FilterSet):
    """Фильтрация ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith',)

    class Meta:
        model = Ingredients
        fields = ('name',)


class TagsFilter(FilterSet):
    """Фильтрация тегов."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
    
    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)