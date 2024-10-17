import random
from string import ascii_letters

from djoser import views as djoser_views
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, api_view

from users.models import User, Subscriber
from recipes.models import (
    Recipes,
    Tags,
    Ingredients,
    ShortLink,
    Favorite,
    ShoppingCart,
    RecipeIngredients
)
from .serializers import (
    RecipeCreateSerializer,
    ShortRecipesSerializer,
    UserSerializer,
    UserCustomSerializer,
    UserAvatarSerializer,
    SubscriptionSerializer,
    RecipesListSerializer,
    TagsSerializer,
    IngredientsSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    ShortLinksSerializer,

)
from .filters import IngredientFilter, TagsFilter
from .paginators import LimitPageNumberPaginator
from .permissions import IsAuthorOrAdminOrReadOnly

SIZE_SHORT_URL = 7


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPaginator
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create',):
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'me', 'retrieve'):
            return UserCustomSerializer
        if self.action in ('set_and_del_avatar'):
            return UserAvatarSerializer
        if self.action in ('subscribe', 'subscriptions'):
            return SubscriptionSerializer
        if self.action in ('set_password'):
            return SetPasswordSerializer
        return UserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def set_and_del_avatar(self, request):
        user = self.request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subcription(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        instance = user.follower.filter(author=author)
        if request.method == 'POST':
            if instance.exists():
                return Response(
                    'Подписка на пользователя есть',
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscriber.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if instance.exists():
                instance.delete()
                return Response(
                    'Подписка удалена',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response('Подписки нет', status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = self.request.user
        subcrubers = User.objects.filter(following__user=user)
        pagination = self.paginate_queryset(subcrubers)
        serializer = SubscriptionSerializer(
            pagination,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    pagination_class = LimitPageNumberPaginator
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    filterset_class = TagsFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipesListSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return ShortRecipesSerializer
        if self.action in ('short-link'):
            pass
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk):
        fav = request.user.favorite.filter(recipe_id=pk)
        if request.method == 'POST':
            if fav.exists():
                return Response(
                    'Рецепт уже в избранном',
                    status=status.HTTP_204_NO_CONTENT
                )
            serializer = FavoriteSerializer(
                Favorite.objects.create(user=request.user, recipe_id=pk)
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if fav.exists():
                fav.delete()
                return Response(
                    'Рецепт удален из избранного',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Рецепт уже удален из избранного',
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        cart = request.user.shopping_cart.filter(recipe_id=pk)
        if request.method == 'POST':
            if cart.exists():
                return Response(
                    'Рецепт уже в списке покупок',
                    status=status.HTTP_204_NO_CONTENT
                )
            serializer = ShoppingCartSerializer(
                ShoppingCart.objects.create(
                    user=request.user,
                    recipe_id=pk
                )
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            if cart.exists():
                cart.delete()
                return Response(
                    'Рецепт удален из списка покупок',
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                'Рецепт уже удален из списка покупок',
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        ingredients_list = RecipeIngredients.objects.filter(
            recipes__in=request.user.shopping_cart.values('recipe')
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(
            sum_amount=Sum('amount')
        )
        shopping_list = 'Список покупок:\n'
        for i, unit in enumerate(ingredients_list, 1):
            shopping_list += (
                f"{i}. {unit['ingredients__name']} - "
                f"{unit['sum_amount']} "
                f"{unit['ingredients__measurement_unit']}\n"
            )
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


@api_view(['GET'])
def short_link(request, recipe_id):
    """Получение короткой ссылки."""
    recipes = get_object_or_404(Recipes, id=recipe_id)
    if ShortLink.objects.filter(
        origin_url=recipes.get_absolute_url()
    ).exists():
        serializer = ShortLinksSerializer(
            ShortLink.objects.get(origin_url=recipes.get_absolute_url())
        )
        return Response(serializer.data)
    domain = request.scheme + "://" + request.META.get('HTTP_HOST') + '/s/'
    short_url = domain + (
        ''.join(random.sample(ascii_letters, SIZE_SHORT_URL))
    )
    link, _ = ShortLink.objects.get_or_create(
        origin_url=recipes.get_absolute_url(),
        short_url=short_url
    )
    serializer = ShortLinksSerializer(link)
    return Response(serializer.data)


def get_full_link(request, short_link):
    """Получение оригинальной ссылки."""
    domain = request.scheme + "://" + get_current_site(request).name + '/s/'
    url = get_object_or_404(ShortLink, short_url=domain + short_link)
    link = url.origin_url.replace('/api', '', 1)[:-1]
    return redirect(link)
