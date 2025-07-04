# Generated by Django 5.2.1 on 2025-06-10 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_remove_post_labor_area_remove_post_labor_references_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='availability_scope',
            field=models.CharField(choices=[('continent', 'Continent-wide'), ('country', 'Country-wide'), ('state', 'State-wide'), ('town', 'Town-specific')], default='town', help_text='Defines the scope of availability for this post (e.g., specific town, entire state, etc.).', max_length=10),
        ),
    ]
