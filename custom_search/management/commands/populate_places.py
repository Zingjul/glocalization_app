from django.core.management.base import BaseCommand
import osmnx as ox
from custom_search.models import State, Town
import networkx as nx

class Command(BaseCommand):
    help = 'Populates towns, cities, and villages from OpenStreetMap'

    def add_arguments(self, parser):
        parser.add_argument('state_name', type=str, help='Name of the state to populate places for')
        parser.add_argument('country_name', type=str, help='Name of the country')

    def handle(self, *args, **options):
        state_name = options['state_name']
        country_name = options['country_name']
        place_name = f"{state_name}, {country_name}"

        try:
            state = State.objects.get(name=state_name)
        except State.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'State "{state_name}" does not exist.'))
            return

        try:
            G = ox.graph_from_place(place_name, tags={'place': ['town', 'city', 'village']})
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error retrieving data from OSM: {e}'))
            return

        for node, data in G.nodes(data=True):
            if 'name' in data:
                place_name = data['name']
                Town.objects.get_or_create(name=place_name, state=state)
                self.stdout.write(self.style.SUCCESS(f'Added place: {place_name}'))