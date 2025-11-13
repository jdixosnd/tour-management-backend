# Generated manually to add snapshot fields to LeadPackage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0005_add_transaction_snapshot_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadpackage',
            name='package_images',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leadpackage',
            name='package_inclusions',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leadpackage',
            name='package_exclusions',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leadpackage',
            name='package_amenities',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leadpackage',
            name='package_policies',
            field=models.JSONField(blank=True, null=True),
        ),
    ]

