from django.core.management.base import BaseCommand
from custom_search.models import Continent

class Command(BaseCommand):
    help = "Populate the database with continents and their codes"

    def handle(self, *args, **kwargs):
        continents = {
            "AF": "Africa",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "SA": "South America",
            "OC": "Oceania",
            "AN": "Antarctica"
        }

        for code, name in continents.items():
            Continent.objects.get_or_create(
                name=name,
                defaults={"code": code}
            )

        self.stdout.write(self.style.SUCCESS("✅ Continents with codes and names populated successfully!"))
