from rest_framework import serializers
from .models import CustomUser
from django_countries import countries

class CountrySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return countries.name(obj.code) # Correctly get country name

class CustomUserSerializer(serializers.ModelSerializer):
    country = CountrySerializer(required=False) # Allow country to be null

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'country', 'state', 'home_town', 'virtual_id']