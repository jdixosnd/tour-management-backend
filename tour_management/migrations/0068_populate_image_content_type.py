from django.db import migrations

def populate_content_type(apps, schema_editor):
    """
    Populate the content_type and object_id fields based on existing module and record_id values.
    """
    ImageMetadata = apps.get_model('tour_management', 'ImageMetadata')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Get ContentType for each model
    Hotel = apps.get_model('tour_management', 'Hotel')
    Room = apps.get_model('tour_management', 'Room')
    Package = apps.get_model('tour_management', 'Package')
    Destination = apps.get_model('tour_management', 'Destination')
    Event = apps.get_model('tour_management', 'Event')
    SightSeeing = apps.get_model('tour_management', 'SightSeeing')
    Cardealer = apps.get_model('tour_management', 'Cardealer')

    hotel_ct = ContentType.objects.get(app_label='tour_management', model='hotel')
    room_ct = ContentType.objects.get(app_label='tour_management', model='room')
    package_ct = ContentType.objects.get(app_label='tour_management', model='package')
    destination_ct = ContentType.objects.get(app_label='tour_management', model='destination')
    event_ct = ContentType.objects.get(app_label='tour_management', model='event')
    sightseeing_ct = ContentType.objects.get(app_label='tour_management', model='sightseeing')
    cardealer_ct = ContentType.objects.get(app_label='tour_management', model='cardealer')

    # Map module names to ContentType objects
    module_to_ct = {
        'hotel': hotel_ct,
        'room': room_ct,
        'package': package_ct,
        'destination': destination_ct,
        'event': event_ct,
        'sightseeing': sightseeing_ct,
        'car_dealer': cardealer_ct,
    }

    # Update each image
    for image in ImageMetadata.objects.all():
        if image.module in module_to_ct:
            image.content_type = module_to_ct[image.module]
            image.object_id = image.record_id

            # Try to get the entity name and type
            try:
                if image.module == 'hotel':
                    entity = Hotel.objects.get(id=image.record_id)
                    image.entity_name = entity.name
                elif image.module == 'room':
                    entity = Room.objects.get(id=image.record_id)
                    image.entity_name = entity.name
                    image.entity_type = entity.type

                    # Get parent entity info for rooms
                    if entity.hotel:
                        image.parent_entity_name = entity.hotel.name
                        image.parent_entity_id = entity.hotel.id
                elif image.module == 'package':
                    entity = Package.objects.get(id=image.record_id)
                    image.entity_name = entity.name
                    image.entity_type = entity.type
                elif image.module == 'destination':
                    entity = Destination.objects.get(id=image.record_id)
                    image.entity_name = entity.name
                elif image.module == 'event':
                    entity = Event.objects.get(id=image.record_id)
                    image.entity_name = entity.name
                elif image.module == 'sightseeing':
                    entity = SightSeeing.objects.get(id=image.record_id)
                    image.entity_name = entity.name
                elif image.module == 'car_dealer':
                    entity = Cardealer.objects.get(id=image.record_id)
                    image.entity_name = entity.name
            except:
                # If entity doesn't exist, just continue
                pass

            image.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0067_auto_20250416_1651'),
    ]

    operations = [
        migrations.RunPython(populate_content_type, migrations.RunPython.noop),
    ]
