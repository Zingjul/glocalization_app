from rest_framework import generics, permissions
from .models import Continent, Country, State, Town
from .serializers import ContinentSerializer, CountrySerializer, StateSerializer, TownSerializer
from person.models import Person
from posts.models import Post
from person.serializers import PersonSerializer
from posts.serializers import PostSerializer
from rest_framework import filters

class ContinentList(generics.ListCreateAPIView):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ContinentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CountryList(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CountryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StateList(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TownList(generics.ListCreateAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TownDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PersonSearch(generics.ListAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['business_name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        continent = self.request.query_params.get('continent')
        country = self.request.query_params.get('country')
        state = self.request.query_params.get('state')
        town = self.request.query_params.get('town')

        if continent:
            queryset = queryset.filter(continent=continent)
        if country:
            queryset = queryset.filter(country=country)
        if state:
            queryset = queryset.filter(state=state)
        if town:
            queryset = queryset.filter(town=town)
        return queryset

class PostSearch(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name', 'product_name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CountryFilter(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        continent_id = self.request.query_params.get('continent_id')
        if continent_id:
            queryset = queryset.filter(continent_id=continent_id)
        return queryset

class StateFilter(generics.ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        country_id = self.request.query_params.get('country_id')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset

class TownFilter(generics.ListAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('state_id')
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        return queryset