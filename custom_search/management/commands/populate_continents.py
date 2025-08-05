from django.core.management.base import BaseCommand
from custom_search.models import Continent

class Command(BaseCommand):
    help = "Populate the database with continents using manual IDs based on dataset"

    def handle(self, *args, **kwargs):
        continents = [
            {"id": 1, "code": "AF", "name": "Africa"},
            {"id": 2, "code": "AM", "name": "Americas"},
            {"id": 3, "code": "AS", "name": "Asia"},
            {"id": 4, "code": "EU", "name": "Europe"},
            {"id": 5, "code": "OC", "name": "Oceania"},
            {"id": 6, "code": "AN", "name": "Antarctica"},  # Polar region
        ]

        for continent in continents:
            obj, created = Continent.objects.update_or_create(
                id=continent["id"],
                defaults={
                    "code": continent["code"],
                    "name": continent["name"]
                }
            )
            action = "✅ Created" if created else "🔄 Updated"
            self.stdout.write(f"{action}: {obj.name} (ID {obj.id})")

        self.stdout.write(self.style.SUCCESS("🌍 Continent table populated successfully with manual IDs."))
