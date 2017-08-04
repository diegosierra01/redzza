from rest_framework import serializers
from .models import Category, WantedCategory, SuggestedCategory


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class WantedCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WantedCategory
        fields = '__all__'


class SuggestedCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SuggestedCategory
        fields = '__all__'
