from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from .models import User, Touroperator,TourOperatorQuota, ImageMetadata, PackageCarDealerMapping,Itineraryitem, PackageHotelMapping, Package, Event, SightSeeing, Packageitineraryitem, DestinationPackageMapping, Hotel, Cardealer, Inclusion, Exclusion
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

        if not all([tour_operator_id, module]):
            return JsonResponse({"error": "tour_operator_id and module are required"}, status=400)

        try:
            # Retrieve tour operator
            tour_operator = Touroperator.objects.get(id=tour_operator_id)

            # Filter images based on tour_operator and module
            images = ImageMetadata.objects.filter(
                tour_operator=tour_operator,
                module=module
            ).order_by("order")

            # Prepare response data
            response_data = [
                {
                    "id": image.id,
                    "description": image.description,
                    "order": image.order,
                    "image_url": image.image_path.url  # Assumes media files are served with .url attribute
                }
                for image in images
            ]

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
