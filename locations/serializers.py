from rest_framework import serializers
from .models import Continent, Country, State, Town

class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = ['id', 'name']

class CountrySerializer(serializers.ModelSerializer):
    continent = serializers.PrimaryKeyRelatedField(queryset=Continent.objects.all())

    class Meta:
        model = Country
        fields = ['id', 'name', 'continent']

    def validate_name(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Country name is too long (max 100 characters).")
        if not value:
            raise serializers.ValidationError("Country name cannot be empty.")
        return value

class StateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = State
        fields = ['id', 'name', 'country']

    def validate_name(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("State name is too long (max 100 characters).")
        if not value:
            raise serializers.ValidationError("State name cannot be empty.")
        return value

class TownSerializer(serializers.ModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())

    class Meta:
        model = Town
        fields = ['id', 'name', 'state']

    def validate_name(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Town name is too long (max 100 characters).")
        if not value:
            raise serializers.ValidationError("Town name cannot be empty.")
        return value