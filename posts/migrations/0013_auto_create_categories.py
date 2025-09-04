# posts/migrations/0002_auto_create_categories.py
from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('posts', 'Category')
    default_categories = ["Labor", "Product", "Service"]
    for name in default_categories:
        Category.objects.get_or_create(name=name)

class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories),
    ]
