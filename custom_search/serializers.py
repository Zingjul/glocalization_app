from rest_framework import serializers
from .models import Continent, Country, State, Town
from django_countries import countries

class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = ['id', 'name']

class CountrySerializer(serializers.ModelSerializer):
    continent = serializers.PrimaryKeyRelatedField(queryset=Continent.objects.all())
    country_name = serializers.SerializerMethodField()
    country_code = serializers.CharField(source='country_code.code')

    class Meta:
        model = Country
        fields = ['id', 'name', 'country_code', 'country_name', 'continent']

    def get_country_name(self, obj):
        return countries.name(obj.country_code)

class StateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = State
        fields = ['id', 'name', 'country']

class TownSerializer(serializers.ModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())

    class Meta:
        model = Town
        fields = ['id', 'name', 'state']