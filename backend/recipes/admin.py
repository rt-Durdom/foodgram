from django.contrib import admin

from recipes.models import Recipes, Tags, Ingredients, RecipeIngredients


class RecipeAdmin(admin.ModelAdmin):
    pass



class TagAdmin(admin.ModelAdmin):
    pass



class IngredientAdmin(admin.ModelAdmin):
    pass


class RecipeIngredientAdmin(admin.ModelAdmin):
    pass

admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientAdmin)
