# Generated by Django 5.2.1 on 2025-07-21 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_search', '0002_pendinglocationrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='continent',
            name='code',
            field=models.CharField(db_index=True, default='TEMP', max_length=5, unique=True),
        ),
        migrations.AddField(
            model_name='country',
            name='code',
            field=models.CharField(db_index=True, default='TEMP', max_length=5, unique=True),
        ),
        migrations.AddField(
            model_name='state',
            name='code',
            field=models.CharField(db_index=True, default='TEMP', max_length=5, unique=True),
        ),
        migrations.AddField(
            model_name='town',
            name='code',
            field=models.CharField(db_index=True, default='TEMP', max_length=5, unique=True),
        ),
        migrations.AlterField(
            model_name='continent',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='country',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='pendinglocationrequest',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='town',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
