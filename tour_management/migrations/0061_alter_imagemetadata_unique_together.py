# Generated by Django 3.2 on 2024-11-08 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0060_touroperatorquota'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='imagemetadata',
            unique_together=set(),
        ),
    ]
