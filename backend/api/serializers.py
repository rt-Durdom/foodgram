from rest_framework import serializers
from users.models import User
from recipes.models import Recipes, Tags, Ingredients, RecipeIngredients, Favorite, ShoppingCart
from django.core.files.base import ContentFile
import base64
from djoser.serializers import UserCreateSerializer, UserSerializer


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


class UserSerializer(UserCreateSerializer):

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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
    measurement_unit = serializers.ReadOnlyField(source='ingredients.measurement_unit')
   

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipesShortSerializer(serializers.ModelSerializer):
    pass


class RecipesListSerializer(serializers.ModelSerializer):
    author = UserCustomSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipesIngredientsSerializer(many=True, read_only=True, source='recipe_ingredients')
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
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.favorite.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
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
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    image = Base64ImageField()

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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(recipes=recipe, amount=ingredient['amount'], ingredients=ingredient['id'])
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredients.objects.create(recipes=instance, amount=ingredient['amount'], ingredients=ingredient['id'])
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)
    
    
    def to_representation(self, instance):
        request = self.context.get('request')
        serializers = RecipesListSerializer(instance, context={'request': request})
        return serializers.data
    



