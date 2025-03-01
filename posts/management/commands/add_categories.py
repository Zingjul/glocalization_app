from django.core.management.base import BaseCommand
from posts.models import Category  # Import your Category model

class Command(BaseCommand):
    help = 'Adds predefined categories to the database'

    def handle(self, *args, **options):
        categories_to_add = [
            "Technology",
            "Travel",
            "Food",
            "Fashion",
            "Sports",
            "Science",
            "Politics",
            "Art",
            "Music",
            "Books",
            # Add more categories here
        ]

        for category_name in categories_to_add:
            # Check if the category already exists to avoid duplicates
            if not Category.objects.filter(name=category_name).exists():
                Category.objects.create(name=category_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully created category: {category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category_name}'))