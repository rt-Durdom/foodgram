from rest_framework import serializers
from users.models import User
from recipes.models import Recipes, Tags, Ingredients, RecipeIngredients
from .validators import validate_username
from django.core.files.base import ContentFile
import base64


class UserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        validators=[validate_username],
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    name = serializers.CharField(source='id.name', read_only=True)
    measurement_unit = serializers.CharField(source='id.measurement_unit', read_only=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

class RecipesShortSerializer(serializers.ModelSerializer):
    pass


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipesIngredientsSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'author',
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


class RecipesListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipesIngredientsSerializer(many=True, read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name ',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_published',
        )



