# Generated by Django 3.0.7 on 2024-10-18 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0009_auto_20241018_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]