# Generated by Django 3.0.7 on 2024-10-16 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0005_auto_20241016_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='country_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='state',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]