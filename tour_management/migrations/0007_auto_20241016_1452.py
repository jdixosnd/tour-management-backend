# Generated by Django 3.0.7 on 2024-10-16 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0006_auto_20241016_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destination',
            name='location_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tour_management.Location'),
        ),
    ]