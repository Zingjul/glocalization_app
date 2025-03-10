from rest_framework import serializers
from .models import Person
from custom_search.serializers import ContinentSerializer, CountrySerializer, StateSerializer, TownSerializer
from django.core.validators import URLValidator

class PersonSerializer(serializers.ModelSerializer):
    continent = ContinentSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    town = TownSerializer(read_only=True)
    website = serializers.CharField(validators=[URLValidator()], allow_blank=True, required=False)
    class Meta:
        model = Person
        fields = ['user', 'business_name', 'person_profile_picture', 'about', 'website', 'use_business_name', 'continent', 'country', 'state', 'town']
        read_only_fields = ['user']