# Generated by Django 5.2.1 on 2025-07-12 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seekers', '0003_seekerpost_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seekerpost',
            name='category',
        ),
        migrations.DeleteModel(
            name='SeekerCategory',
        ),
    ]
