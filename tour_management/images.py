from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from .models import User, Touroperator,TourOperatorQuota, ImageMetadata, PackageCarDealerMapping,Itineraryitem, PackageHotelMapping, Package, Event, SightSeeing, Packageitineraryitem, DestinationPackageMapping, Cardealer, Inclusion, Exclusion, Hotel, Room, Destination
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from collections import defaultdict
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from collections import defaultdict
from django.db import transaction
import json
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from django.conf import settings

@csrf_exempt
def upload_images(request):
    if request.method == 'POST':
        tour_operator_id = request.POST.get("tour_operator_id")
        module = request.POST.get("module")
        record_id = request.POST.get("record_id")
        descriptions = request.POST.getlist("description", [])
        orders = request.POST.getlist("order", [])

        # Validate required fields
        if not all([tour_operator_id, module, record_id, request.FILES.getlist("images")]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        try:
            # Get tour operator and check quota
            tour_operator = Touroperator.objects.get(id=tour_operator_id)
            quota_field = f"max_images_{module}"
            max_images = getattr(TourOperatorQuota.objects.get(tour_operator=tour_operator), quota_field, 5)

            # Check current image count for the module and record
            current_count = ImageMetadata.objects.filter(
                tour_operator=tour_operator,
                module=module,
                record_id=record_id
            ).count()
            if current_count >= max_images:
                return JsonResponse({"error": "Quota exceeded for image uploads"}, status=400)

            # Process each image
            images = request.FILES.getlist("images")
            response_data = []
            for index, image_file in enumerate(images):
                # Verify quota
                if current_count + index >= max_images:
                    response_data.append({
                        "error": f"Quota exceeded. Only {max_images - current_count} images can be uploaded.",
                        "file_name": image_file.name
                    })
                    continue

                # Compress image
                img = Image.open(image_file)
                img_io = io.BytesIO()
                img.save(img_io, format="JPEG", quality=75)
                img_io.seek(0)
                compressed_image = InMemoryUploadedFile(
                    img_io,
                    'ImageField',
                    f"{image_file.name.split('.')[0]}.jpg",
                    'image/jpeg',
                    img_io.getbuffer().nbytes,
                    None
                )

                # Get description and order for each image, if provided
                description = descriptions[index] if index < len(descriptions) else ""
                order = orders[index] if index < len(orders) else index

                # Save image and metadata
                image_metadata = ImageMetadata.objects.create(
                    tour_operator=tour_operator,
                    module=module,
                    record_id=record_id,
                    image_path=compressed_image,
                    description=description,
                    order=order
                )

                # Update the image_ids field of the corresponding entity
                if module == 'hotel':
                    try:
                        hotel = Hotel.objects.get(id=record_id)
                        if hotel.image_ids is None:
                            hotel.image_ids = []
                        hotel.image_ids.append(image_metadata.id)
                        hotel.save(update_fields=['image_ids'])
                    except Hotel.DoesNotExist:
                        pass
                elif module == 'room':
                    try:
                        room = Room.objects.get(id=record_id)
                        if room.image_ids is None:
                            room.image_ids = []
                        room.image_ids.append(image_metadata.id)
                        room.save(update_fields=['image_ids'])
                    except Room.DoesNotExist:
                        pass
                elif module == 'package':
                    try:
                        package = Package.objects.get(id=record_id)
                        if package.image_ids is None:
                            package.image_ids = []
                        package.image_ids.append(image_metadata.id)
                        package.save(update_fields=['image_ids'])
                    except Package.DoesNotExist:
                        pass
                elif module == 'destination':
                    try:
                        destination = Destination.objects.get(id=record_id)
                        if destination.image_ids is None:
                            destination.image_ids = []
                        destination.image_ids.append(image_metadata.id)
                        destination.save(update_fields=['image_ids'])
                    except Destination.DoesNotExist:
                        pass
                elif module == 'car_dealer':
                    try:
                        cardealer = Cardealer.objects.get(id=record_id)
                        if cardealer.image_ids is None:
                            cardealer.image_ids = []
                        cardealer.image_ids.append(image_metadata.id)
                        cardealer.save(update_fields=['image_ids'])
                    except Cardealer.DoesNotExist:
                        pass
                elif module == 'event':
                    try:
                        event = Event.objects.get(id=record_id)
                        if event.image_ids is None:
                            event.image_ids = []
                        event.image_ids.append(image_metadata.id)
                        event.save(update_fields=['image_ids'])
                    except Event.DoesNotExist:
                        pass
                elif module == 'sightseeing':
                    try:
                        sightseeing = SightSeeing.objects.get(id=record_id)
                        if sightseeing.image_ids is None:
                            sightseeing.image_ids = []
                        sightseeing.image_ids.append(image_metadata.id)
                        sightseeing.save(update_fields=['image_ids'])
                    except SightSeeing.DoesNotExist:
                        pass

                response_data.append({
                    "message": "Image uploaded successfully",
                    "image_id": image_metadata.id,
                    "file_name": image_file.name
                })

            return JsonResponse({"results": response_data}, status=201)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except TourOperatorQuota.DoesNotExist:
            return JsonResponse({"error": "Quota configuration missing for the tour operator"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def get_images(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Validate required fields
        tour_operator_id = data.get("tour_operator_id")
        module = data.get("module")
        record_id = data.get("record_id")  # Optional: specific record ID
        include_binary = data.get("include_binary", False)  # Optional: include binary data

        if not all([tour_operator_id, module]):
            return JsonResponse({"error": "tour_operator_id and module are required"}, status=400)

        try:
            # Retrieve tour operator
            tour_operator = Touroperator.objects.get(id=tour_operator_id)

            # Get the entity based on the module and record_id
            entity = None
            if record_id:
                if module == 'hotel':
                    entity = Hotel.objects.filter(id=record_id).first()
                elif module == 'room':
                    entity = Room.objects.filter(id=record_id).first()
                elif module == 'package':
                    entity = Package.objects.filter(id=record_id).first()
                elif module == 'destination':
                    entity = Destination.objects.filter(id=record_id).first()
                elif module == 'car_dealer':
                    entity = Cardealer.objects.filter(id=record_id).first()
                elif module == 'event':
                    entity = Event.objects.filter(id=record_id).first()
                elif module == 'sightseeing':
                    entity = SightSeeing.objects.filter(id=record_id).first()

            # If entity is found and has image_ids, use them to fetch images
            if entity and entity.image_ids:
                images = ImageMetadata.objects.filter(id__in=entity.image_ids).order_by("order")
            else:
                # Build query filter
                query_filter = {
                    'tour_operator': tour_operator,
                    'module': module
                }

                # Add record_id filter if provided
                if record_id:
                    query_filter['record_id'] = record_id

                # Filter images based on criteria
                images = ImageMetadata.objects.filter(**query_filter).order_by("order")

            # Prepare response data
            response_data = []
            for image in images:
                image_data = {
                    "id": image.id,
                    "description": image.description,
                    "order": image.order,
                    "image_url": image.image_path.url  # Assumes media files are served with .url attribute
                }

                # Include binary data if requested
                if include_binary:
                    try:
                        import base64
                        with open(image.image_path.path, 'rb') as img_file:
                            image_data["image_binary"] = base64.b64encode(img_file.read()).decode('utf-8')
                    except Exception as e:
                        # If there's an error reading the file, continue without binary data
                        image_data["image_binary_error"] = str(e)

                response_data.append(image_data)

            return JsonResponse({"images": response_data}, status=200)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def delete_image(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Check if image_id is provided in the request
        image_id = data.get("image_id")
        if not image_id:
            return JsonResponse({"error": "image_id is required"}, status=400)

        try:
            # Retrieve the image entry from the database
            image = ImageMetadata.objects.get(id=image_id)

            # Remove the image ID from the image_ids field of the corresponding entity
            module = image.module
            record_id = image.record_id

            if module == 'hotel':
                try:
                    hotel = Hotel.objects.get(id=record_id)
                    if hotel.image_ids and image_id in hotel.image_ids:
                        hotel.image_ids.remove(image_id)
                        hotel.save(update_fields=['image_ids'])
                except Hotel.DoesNotExist:
                    pass
            elif module == 'room':
                try:
                    room = Room.objects.get(id=record_id)
                    if room.image_ids and image_id in room.image_ids:
                        room.image_ids.remove(image_id)
                        room.save(update_fields=['image_ids'])
                except Room.DoesNotExist:
                    pass
            elif module == 'package':
                try:
                    package = Package.objects.get(id=record_id)
                    if package.image_ids and image_id in package.image_ids:
                        package.image_ids.remove(image_id)
                        package.save(update_fields=['image_ids'])
                except Package.DoesNotExist:
                    pass
            elif module == 'destination':
                try:
                    destination = Destination.objects.get(id=record_id)
                    if destination.image_ids and image_id in destination.image_ids:
                        destination.image_ids.remove(image_id)
                        destination.save(update_fields=['image_ids'])
                except Destination.DoesNotExist:
                    pass
            elif module == 'car_dealer':
                try:
                    cardealer = Cardealer.objects.get(id=record_id)
                    if cardealer.image_ids and image_id in cardealer.image_ids:
                        cardealer.image_ids.remove(image_id)
                        cardealer.save(update_fields=['image_ids'])
                except Cardealer.DoesNotExist:
                    pass
            elif module == 'event':
                try:
                    event = Event.objects.get(id=record_id)
                    if event.image_ids and image_id in event.image_ids:
                        event.image_ids.remove(image_id)
                        event.save(update_fields=['image_ids'])
                except Event.DoesNotExist:
                    pass
            elif module == 'sightseeing':
                try:
                    sightseeing = SightSeeing.objects.get(id=record_id)
                    if sightseeing.image_ids and image_id in sightseeing.image_ids:
                        sightseeing.image_ids.remove(image_id)
                        sightseeing.save(update_fields=['image_ids'])
                except SightSeeing.DoesNotExist:
                    pass

            # Capture the image path before deletion
            image_path = os.path.join(settings.MEDIA_ROOT, str(image.image_path))

            # Delete the entry from the database
            image.delete()

            # Check if file exists on the server and remove it
            if os.path.exists(image_path):
                os.remove(image_path)
            else:
                return JsonResponse({"warning": "Image file not found on server"}, status=200)

            return JsonResponse({"message": "Image deleted successfully"}, status=200)

        except ImageMetadata.DoesNotExist:
            return JsonResponse({"error": "Image entry not found in the database"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
