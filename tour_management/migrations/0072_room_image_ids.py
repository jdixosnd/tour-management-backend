from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0071_merge_0069_auto_20250416_1659_0070_auto_20250416_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='image_ids',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='package',
            name='image_ids',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='image_ids',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='image_ids',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sightseeing',
            name='image_ids',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cardealer',
            name='image_ids',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
