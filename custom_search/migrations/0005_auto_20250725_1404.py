# THIS FILE IS NO LONGER NEEDED
# I CANT DELETE IT BECAUSE IT WILL RAISE ERRORS
# IT WAS CREATED IN ORDER TO POPULATE THE DATABASE IT 'UNSPECIFIED' ON EACH FIELD OF DIFFERENT LOCATIONS WITH ID=1
# BUT SINCE WE ARE NOW MANUALLY GIVING EACH ENTRY IT'S ID (THANKS TO THE INDIAN DATABASE). WE NO LONGER NEED TO USE THIS FILE
# FOR THAT REASON I AM DISABLING THE LINE THAT MAKES THIS CODE RUN ON MIGRATION

from django.db import migrations

def create_defaults(apps, schema_editor):
    Continent = apps.get_model("custom_search", "Continent")
    Country = apps.get_model("custom_search", "Country")
    State = apps.get_model("custom_search", "State")
    Town = apps.get_model("custom_search", "Town")

    unspecified_continent, _ = Continent.objects.update_or_create(
        code="unspecified",
        defaults={"name": "Unspecified"}
    )

    unspecified_country, _ = Country.objects.update_or_create(
        code="unspecified",
        defaults={
            "name": "Unspecified",
            "continent": unspecified_continent,
            "country_code": "UNSPE"  # Use ZZ or a rarely used country code
        }
    )

    unspecified_state, _ = State.objects.update_or_create(
        code="unspecified",
        defaults={
            "name": "Unspecified",
            "country": unspecified_country
        }
    )

    Town.objects.update_or_create(
        code="unspecified",
        defaults={
            "name": "Unspecified",
            "state": unspecified_state,
            "type": "town"
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('custom_search', '0004_alter_state_id'),
    ]

    operations = [
        # LINE DIABLED
        # migrations.RunPython(create_defaults),
    ]
