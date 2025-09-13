from django.core.management.base import BaseCommand
from posts.models import Category
from seekers.models import SeekerCategory


class Command(BaseCommand):
    help = "Add default categories to both Posts and Seekers apps"

    def handle(self, *args, **kwargs):
        categories = ["Product", "Service", "Labor"]

        # --- Populate Posts app categories ---
        self.stdout.write(self.style.MIGRATE_HEADING("Populating Posts categories..."))
        for cat_name in categories:
            obj, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"[Posts] Category '{cat_name}' created."))
            else:
                self.stdout.write(f"[Posts] Category '{cat_name}' already exists.")

        # --- Populate Seekers app categories ---
        self.stdout.write(self.style.MIGRATE_HEADING("Populating Seekers categories..."))
        for cat_name in categories:
            obj, created = SeekerCategory.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"[Seekers] Category '{cat_name}' created."))
            else:
                self.stdout.write(f"[Seekers] Category '{cat_name}' already exists.")

        self.stdout.write(self.style.SUCCESS("✅ All categories added/verified in Posts and Seekers."))
