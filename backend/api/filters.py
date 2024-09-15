class IngredientFilter(FilterSet):
    """Фильтрация ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith',)

    class Meta:
        model = Ingredient
        fields = ('name',)