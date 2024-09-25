from django.contrib import admin

from recipes.models import Recipes, Tags, Ingredients, RecipeIngredients


class TagAdmin(admin.ModelAdmin):
    pass


class IngredientAdmin(admin.ModelAdmin):
    pass


class RecipeIngredientsInLine(admin.StackedInline):
    model = RecipeIngredients
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientsInLine]
    exclude = ('inredients', )


admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(Ingredients, IngredientAdmin)
