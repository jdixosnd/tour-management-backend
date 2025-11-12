# Generated migration for adding image support to ItineraryItem

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0003_auto_20251110_0657'),
    ]

    operations = [
        # Note: image_ids field already exists in Itineraryitem table from previous migration attempt
        # Update ImageMetadata MODULE_CHOICES to include itinerary_item
        migrations.AlterField(
            model_name='imagemetadata',
            name='module',
            field=models.CharField(
                choices=[
                    ('destination', 'Destination'),
                    ('package', 'Package'),
                    ('hotel', 'Hotel'),
                    ('room', 'Room'),
                    ('car_dealer', 'Car Dealer'),
                    ('event', 'Event'),
                    ('sightseeing', 'Sightseeing'),
                    ('itinerary_item', 'Itinerary Item'),
                ],
                max_length=50
            ),
        ),
        # Add max_images_itinerary_item field to TourOperatorQuota
        migrations.AddField(
            model_name='touroperatorquota',
            name='max_images_itinerary_item',
            field=models.PositiveIntegerField(default=5),
        ),
    ]

