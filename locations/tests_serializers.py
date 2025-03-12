import unittest
from location.serializers import ContinentSerializer, CountrySerializer, StateSerializer, TownSerializer
from location.models import Continent, Country, State, Town

class LocationSerializerTests(unittest.TestCase):

    def setUp(self):
        self.continent = Continent.objects.create(name='Test Continent')
        self.country = Country.objects.create(name='Test Country', continent=self.continent)
        self.state = State.objects.create(name='Test State', country=self.country)
        self.town = Town.objects.create(name='Test Town', state=self.state)

    def test_continent_serializer(self):
        serializer = ContinentSerializer(self.continent)
        self.assertEqual(serializer.data['name'], 'Test Continent')

    def test_country_serializer(self):
        serializer = CountrySerializer(self.country)
        self.assertEqual(serializer.data['name'], 'Test Country')

    def test_state_serializer(self):
        serializer = StateSerializer(self.state)
        self.assertEqual(serializer.data['name'], 'Test State')

    def test_town_serializer(self):
        serializer = TownSerializer(self.town)
        self.assertEqual(serializer.data['name'], 'Test Town')