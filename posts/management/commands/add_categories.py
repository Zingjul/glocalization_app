from django.core.management.base import BaseCommand
from posts.models import Category

class Command(BaseCommand):
    help = 'Populates the Category model with default categories'

    def handle(self, *args, **options):
        categories = ['Goods', 'Services', 'Labor']
        for category_name in categories:
            if not Category.objects.filter(name=category_name).exists():
                Category.objects.create(name=category_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully created category: {category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category {category_name} already exists.'))