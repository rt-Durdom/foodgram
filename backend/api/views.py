from djoser import views as djoser_views

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from users.models import User
from recipes.models import Recipes, Tags, Ingredients, RecipeIngredients, Favorite, ShoppingCart
from .serializers import (
    RecipeCreateSerializer,
    ShortRecipesSerializer,
    UserSerializer,
    RecipesListSerializer,
    TagsSerializer,
    IngredientsSerializer,
)
from .filters import IngredientFilter
from .paginators import LimitPageNumberPaginator
from .permissions import IsAuthorOrAdminOrReadOnly


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):  # +
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):  # +
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter



class RecipesViewSet(viewsets.ModelViewSet):  # filter

    queryset = Recipes.objects.all()
    pagination_class = LimitPageNumberPaginator
    permission_classes = (IsAuthorOrAdminOrReadOnly, )


    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipesListSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return ShortRecipesSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated], url_path='favorite')
    def favorite(self, request, pk):
        fav = Favorite.objects.filter(user=request.user, recipe_id=pk)
        if request.method == 'POST':

            if fav.exists():
                return Response('Рецепт уже в избранном', status=status.HTTP_204_NO_CONTENT)
            else:
                serializer = self.get_serializer(Favorite.objects.create(user=request.user, recipe_id=pk))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if fav.exists():
                fav.delete()
                return Response('Рецепт удален из избранного', status=status.HTTP_204_NO_CONTENT)
            return Response('Рецепт уже удален из избранного', status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated], url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        cart = ShoppingCart.objects.filter(user=request.user, recipe_id=pk)
        if request.method == 'POST':
            if cart.exists():
                return Response('Рецепт уже в корзине', status=status.HTTP_204_NO_CONTENT)
            else:
                serializer = self.get_serializer(ShoppingCart.objects.create(user=request.user, recipe_id=pk))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if cart.exists():
                cart.delete()
                return Response('Рецепт удален из корзины', status=status.HTTP_204_NO_CONTENT)
            return Response('Рецепт уже удален из корзины', status=status.HTTP_400_BAD_REQUEST)