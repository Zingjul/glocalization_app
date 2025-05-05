from django.core.management.base import BaseCommand
from custom_search.models import Continent

class Command(BaseCommand):
    help = "Populate the database with continents"

    def handle(self, *args, **kwargs):
        continents = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Antarctica"]
        
        for name in continents:
            Continent.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("✅ Continents added successfully!"))
