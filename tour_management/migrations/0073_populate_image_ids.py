from django.db import migrations

def populate_image_ids(apps, schema_editor):
    """
    Populate the image_ids fields of existing entities based on the existing ImageMetadata records.
    """
    ImageMetadata = apps.get_model('tour_management', 'ImageMetadata')
    Hotel = apps.get_model('tour_management', 'Hotel')
    Room = apps.get_model('tour_management', 'Room')
    Package = apps.get_model('tour_management', 'Package')
    Destination = apps.get_model('tour_management', 'Destination')
    Cardealer = apps.get_model('tour_management', 'Cardealer')
    Event = apps.get_model('tour_management', 'Event')
    SightSeeing = apps.get_model('tour_management', 'SightSeeing')
    
    # Process hotel images
    hotel_images = ImageMetadata.objects.filter(module='hotel')
    for image in hotel_images:
        try:
            hotel = Hotel.objects.get(id=image.record_id)
            if hotel.image_ids is None:
                hotel.image_ids = []
            if image.id not in hotel.image_ids:
                hotel.image_ids.append(image.id)
                hotel.save()
        except Hotel.DoesNotExist:
            pass
    
    # Process room images
    room_images = ImageMetadata.objects.filter(module='room')
    for image in room_images:
        try:
            room = Room.objects.get(id=image.record_id)
            if room.image_ids is None:
                room.image_ids = []
            if image.id not in room.image_ids:
                room.image_ids.append(image.id)
                room.save()
        except Room.DoesNotExist:
            pass
    
    # Process package images
    package_images = ImageMetadata.objects.filter(module='package')
    for image in package_images:
        try:
            package = Package.objects.get(id=image.record_id)
            if package.image_ids is None:
                package.image_ids = []
            if image.id not in package.image_ids:
                package.image_ids.append(image.id)
                package.save()
        except Package.DoesNotExist:
            pass
    
    # Process destination images
    destination_images = ImageMetadata.objects.filter(module='destination')
    for image in destination_images:
        try:
            destination = Destination.objects.get(id=image.record_id)
            if destination.image_ids is None:
                destination.image_ids = []
            if image.id not in destination.image_ids:
                destination.image_ids.append(image.id)
                destination.save()
        except Destination.DoesNotExist:
            pass
    
    # Process car dealer images
    cardealer_images = ImageMetadata.objects.filter(module='car_dealer')
    for image in cardealer_images:
        try:
            cardealer = Cardealer.objects.get(id=image.record_id)
            if cardealer.image_ids is None:
                cardealer.image_ids = []
            if image.id not in cardealer.image_ids:
                cardealer.image_ids.append(image.id)
                cardealer.save()
        except Cardealer.DoesNotExist:
            pass
    
    # Process event images
    event_images = ImageMetadata.objects.filter(module='event')
    for image in event_images:
        try:
            event = Event.objects.get(id=image.record_id)
            if event.image_ids is None:
                event.image_ids = []
            if image.id not in event.image_ids:
                event.image_ids.append(image.id)
                event.save()
        except Event.DoesNotExist:
            pass
    
    # Process sightseeing images
    sightseeing_images = ImageMetadata.objects.filter(module='sightseeing')
    for image in sightseeing_images:
        try:
            sightseeing = SightSeeing.objects.get(id=image.record_id)
            if sightseeing.image_ids is None:
                sightseeing.image_ids = []
            if image.id not in sightseeing.image_ids:
                sightseeing.image_ids.append(image.id)
                sightseeing.save()
        except SightSeeing.DoesNotExist:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0072_room_image_ids'),
    ]

    operations = [
        migrations.RunPython(populate_image_ids, migrations.RunPython.noop),
    ]
