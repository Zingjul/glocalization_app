from django.core.management.base import BaseCommand
from posts.models import Category

class Command(BaseCommand):
    help = "Add default categories to the database"

    def handle(self, *args, **kwargs):
        categories = [
            "Product",
            "Service",
            "Labor",
        ]

        for cat_name in categories:
            obj, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Category '{cat_name}' created."))
            else:
                self.stdout.write(f"Category '{cat_name}' already exists.")

        self.stdout.write(self.style.SUCCESS("All categories added/verified."))
