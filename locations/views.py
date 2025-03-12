from rest_framework import generics, permissions, serializers
from .models import Continent, Country, State, Town
from .serializers import ContinentSerializer, CountrySerializer, StateSerializer, TownSerializer
from .permissions import IsAdminOrReadOnly

class ContinentList(generics.ListCreateAPIView):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    permission_classes = [IsAdminOrReadOnly]

class ContinentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    permission_classes = [IsAdminOrReadOnly]

class CountryList(generics.ListCreateAPIView):
    queryset = Country.objects.select_related('continent').all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]

class CountryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.select_related('continent').all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]

class StateList(generics.ListCreateAPIView):
    queryset = State.objects.select_related('country__continent', 'country').all()
    serializer_class = StateSerializer
    permission_classes = [IsAdminOrReadOnly]

class StateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.select_related('country__continent', 'country').all()
    serializer_class = StateSerializer
    permission_classes = [IsAdminOrReadOnly]

class TownList(generics.ListCreateAPIView):
    queryset = Town.objects.select_related('state__country__continent', 'state__country', 'state').all()
    serializer_class = TownSerializer
    permission_classes = [IsAdminOrReadOnly]

class TownDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Town.objects.select_related('state__country__continent', 'state__country', 'state').all()
    serializer_class = TownSerializer
    permission_classes = [IsAdminOrReadOnly]