# Generated by Django 3.2 on 2024-11-04 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0051_auto_20241104_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadpackage',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.user'),
        ),
    ]