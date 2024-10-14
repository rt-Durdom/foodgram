from django.contrib import admin

from recipes.models import Recipes, Tags, Ingredients, RecipeIngredients


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class RecipeIngredientsInLine(admin.StackedInline):
    model = RecipeIngredients
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInLine]
    exclude = ('inredients', )
    list_display = ('name', 'author', 'count_favorite')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def count_favorite(self, obj):
        return obj.favorites.count()


admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(Ingredients, IngredientAdmin)
