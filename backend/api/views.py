from djoser import views as djoser_views

from rest_framework import viewsets

from users.models import User
from recipes.models import Recipes, Tags, Ingredients
from .serializers import (
    RecipeCreateSerializer,
    RecipesShortSerializer,
    UserSerializer,
    RecipesListSerializer,
    TagsSerializer,
    IngredientsSerializer,
)


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    RECIPES_IN_FAVORITE = 'Рецепт уже в избранном'
    RECIPES_IN_SHOPPING_CART = 'Рецепт уже в списке покупок'
    queryset = Recipes.objects.all()
    serializer_class = RecipesListSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ('list' or 'retrieve'):
            return RecipesListSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return RecipesShortSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
