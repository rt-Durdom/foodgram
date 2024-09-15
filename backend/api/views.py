from djoser import views as djoser_views

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny

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
from .paginators import LimitPageNumberPaginator
from .permissions import IsAuthorOrAdminOrReadOnly


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):  # +
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):  # filter
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):  # filter

    queryset = Recipes.objects.all()
    pagination_class = LimitPageNumberPaginator
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    #filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipesListSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return RecipesShortSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
