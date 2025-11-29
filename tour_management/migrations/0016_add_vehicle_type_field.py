# Generated migration for adding vehicle_type field to package options and transactions
# This migration adds vehicle_type field to replace transportation module dependencies

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0015_add_transport_to_package_options'),
    ]

    operations = [
        # Add vehicle_type field to PackageOption
        migrations.AddField(
            model_name='packageoption',
            name='vehicle_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        
        # Add vehicle_type field to LeadPackageOption
        migrations.AddField(
            model_name='leadpackageoption',
            name='vehicle_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        
        # Add vehicle_type field to TransactionItineraryItem
        migrations.AddField(
            model_name='transactionitineraryitem',
            name='vehicle_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

