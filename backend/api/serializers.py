from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.files.base import ContentFile
import base64
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.core.validators import RegexValidator, MinValueValidator

from users.models import User
from recipes.models import (
    Recipes,
    Tags,
    Ingredients,
    RecipeIngredients,
    Favorite,
    ShoppingCart,
    ShortLink,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = (
            'avatar',
        )


class UserCustomSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user, author=obj).exists()


class ShortRecipesSerializer(serializers.ModelSerializer):

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(UserCustomSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed',
            'avatar',
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializers = ShortRecipesSerializer(recipes, many=True)
        return serializers.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Такой пользователь существует',
            ),
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Вы ввели недопустимые символы',
            ),
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
        )]
    )
    first_name = serializers.CharField(
        max_length=150
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipesIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ShortLinksSerializer(serializers.ModelSerializer):
    short_link = serializers.CharField(source='short_url')

    class Meta:
        model = ShortLink
        fields = ('short_link',)

    def to_representation(self, value):
        return {'short-link': value.short_url}


class RecipesListSerializer(serializers.ModelSerializer):
    author = UserCustomSerializer(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipesIngredientsSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.favorite.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class CreateIngredientSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    amount = serializers.IntegerField(min_value=1, write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):

    ingredients = CreateIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=([MinValueValidator(1)]),
    )

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        sum_ingredients = set()
        for ingredient in value:
            if ingredient['id'] in sum_ingredients:
                raise serializers.ValidationError(
                    'Два одинаковых ингредиента - один необходимо удалить'
                )
            sum_ingredients.add(ingredient['id'])
        for ingredient in value:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля'
                )
        return value

    def get_recipe_ingedients_create(self, obj, val_ingredients):
        list_ingred = [RecipeIngredients(
            recipes=obj,
            amount=ingredient['amount'],
            ingredients=ingredient['id']
        ) for ingredient in val_ingredients]
        return RecipeIngredients.objects.bulk_create(list_ingred)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег'
            )
        sum_tags = set()
        for tag in tags:
            id_tag = tag
            if id_tag in sum_tags:
                raise serializers.ValidationError(
                    'Два одинаковых тега - один необходимо удалить'
                )
            else:
                sum_tags.add(id_tag)
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.get_recipe_ingedients_create(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError('Нет ингредиентов')
        if 'tags' not in validated_data:
            raise serializers.ValidationError('Нет тегов')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if not tags:
            raise serializers.ValidationError(
                'Список тегов пуст - необходимо добавить хотя бы один тег'
            )
        sum_tags = set()
        for tag in tags:
            if tag in sum_tags:
                raise serializers.ValidationError(
                    'Два одинаковых тега - один необходимо удалить'
                )
            sum_tags.add(tag)
        instance.ingredients.clear()
        self.get_recipe_ingedients_create(instance, ingredients)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        serializers = RecipesListSerializer(
            instance, context={'request': request}
        )
        return serializers.data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )
