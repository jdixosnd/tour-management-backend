# Generated by Django 3.2 on 2024-11-04 10:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0054_auto_20241104_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaditineraryitem',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.user'),
        ),
    ]
