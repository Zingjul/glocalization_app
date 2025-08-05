# populate_continents.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings') #replace your_project_name
import django
django.setup()

from custom_search.models import Continent

continents = ["North America", "Europe", "Africa", "Asia", "South America", "Australia", "Antarctica"]

for continent_name in continents:
    Continent.objects.get_or_create(name=continent_name)
    print(f"Added continent: {continent_name}")