# Generated by Django 3.0.7 on 2024-10-31 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0030_auto_20241031_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
