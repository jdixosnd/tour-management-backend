from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import Destination, StateCityToDestinationMapping,StateCity,Touroperator, User, Location, LeadDestinationMapping, Transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from django.http import JsonResponse
from django.db import transaction


def add_destination(request):
    required_keys = ["tour_operator_id", "user_id", "name"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            return JsonResponse({"error": ",".join(required_keys) + " are required fields."}, status=400)

        # At least one of locations or location_ids must be provided
        if not data.get('locations') and not data.get('location_ids'):
            return JsonResponse({"error": "Either 'locations' or 'location_ids' must be provided."}, status=400)

        try:
            with transaction.atomic():
                touroperator = Touroperator.objects.get(uuid=data['tour_operator_id'])
                user = User.objects.get(uuid=data['user_id'])

                if Destination.objects.filter(tour_operator_id=touroperator, name=data['name']).exists():
                    return JsonResponse({"error": "The destination already exists."}, status=409)

                destination = Destination.objects.create(
                    tour_operator_id=touroperator,
                    created_by=user,
                    name=data['name'],
                    description=data.get('description', '')
                )

                locations_data = []

                # Process location_ids if provided (map existing locations)
                if data.get('location_ids'):
                    for location_id in data['location_ids']:
                        location = Location.objects.get(uuid=location_id, tour_operator=touroperator)

                        # Get or create StateCity for this location
                        statecity, _ = StateCity.objects.get_or_create(
                            state__iexact=location.state,
                            city__iexact=location.city,
                            defaults={
                                'state': location.state,
                                'city': location.city
                            }
                        )

                        # Create mapping
                        StateCityToDestinationMapping.objects.create(
                            state_city=statecity,
                            destination=destination,
                            location=location
                        )

                        locations_data.append({
                            "id": str(location.uuid),
                            "name": location.name,
                            "city": location.city,
                            "state": location.state,
                            "country": location.country,
                            "pin_code": location.pin_code,
                            "address": location.address,
                            "lng": float(location.lng) if location.lng else None,
                            "lat": float(location.lat) if location.lat else None
                        })

                # Process locations array if provided (create new or use existing)
                if data.get('locations'):
                    for location_data in data['locations']:
                        # Get or create StateCity
                        statecity, _ = StateCity.objects.get_or_create(
                            state__iexact=location_data['state'],
                            city__iexact=location_data['city'],
                            defaults={
                                'state': location_data['state'],
                                'city': location_data['city']
                            }
                        )

                        # If location_id is provided, use existing location
                        if 'location_id' in location_data and location_data['location_id']:
                            location = Location.objects.get(uuid=location_data['location_id'])
                        else:
                            # Create or get Location object with full details
                            location, created = Location.objects.get_or_create(
                                tour_operator=touroperator,
                                name=location_data.get('name', f"{location_data['city']}, {location_data['state']}"),
                                city=location_data['city'],
                                state=location_data['state'],
                                country=location_data.get('country', ''),
                                defaults={
                                    'created_by': user,
                                    'pin_code': location_data.get('pin_code'),
                                    'address': location_data.get('address'),
                                    'lng': location_data.get('lng'),
                                    'lat': location_data.get('lat')
                                }
                            )

                        # Create mapping with both StateCity and Location
                        StateCityToDestinationMapping.objects.create(
                            state_city=statecity,
                            destination=destination,
                            location=location
                        )

                        locations_data.append({
                            "id": str(location.uuid),
                            "name": location.name,
                            "city": location.city,
                            "state": location.state,
                            "country": location.country,
                            "pin_code": location.pin_code,
                            "address": location.address,
                            "lng": float(location.lng) if location.lng else None,
                            "lat": float(location.lat) if location.lat else None
                        })

                result = {
                    "id": str(destination.uuid),
                    "name": destination.name,
                    "description": destination.description,
                    "created_by_id": str(destination.created_by.uuid),
                    "tour_operator_id": str(destination.tour_operator_id.uuid),
                    "locations": locations_data,
                    "location_ids": [loc["id"] for loc in locations_data],
                    "image_ids": destination.image_ids if destination.image_ids else []
                }

                return JsonResponse(result, status=201)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Location.DoesNotExist:
            return JsonResponse({"error": "Invalid location ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


"""def get_destinations(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        user_id = None
        tour_operator_id = None
        if 'user_id' in data:
            user_id = data['user_id']

        if 'tour_operator_id' in data:
            tour_operator_id = data['tour_operator_id']

        if user_id is None and tour_operator_id is None:
            return HttpResponseBadRequest(json.dumps({
            "status":"failed",
            "code":400,
            "message": "User_id or tour_operator_id is required"}), content_type='application/json')
        
        if user_id is not None:
            destination = Destination.objects.filter(id=user_id)
        elif tour_operator_id is not None:
            destination = Destination.objects.filter(tour_operator_id=tour_operator_id)
        else:
            destination = Destination.objects.all()

        for dest in destination:
            result.append({"id":dest.id,
                           "name":dest.name,
                           "description":dest.description,
                           "created_by_id":dest.created_by.id,
                           "tour_operator_id":dest.tour_operator_id.id,
                           "location":{
                               "id":dest.location_id.id,
                               "name":dest.location_id.name,
                               "description":dest.location_id.description,
                               "city":dest.location_id.city,
                               "state":dest.location_id.city,
                               "country":dest.location_id.country,
                               "pin_code":dest.location_id.pin_code,
                               "created_by_id":dest.location_id.created_by.id,
                               "lat":float(dest.location_id.lat),
                               "lng":float(dest.location_id.lng),
                               "tour_operator_id":dest.location_id.tour_operator.id
                           }})

        return HttpResponse(json.dumps({
            "status":"sucess",
            "code":200,
            "message": "Fetched destination records successfully",
            "data":result}), content_type='application/json')
"""

def update_destination(request):
    required_keys = ["id", "tour_operator_id", "user_id", "name"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()

        # Check for missing keys
        if missing_keys:
            return JsonResponse({"error": ",".join(required_keys) + " are required fields."}, status=400)

        try:
            with transaction.atomic():
                # Get the destination to update
                destination = Destination.objects.get(uuid=data['id'])
                touroperator = Touroperator.objects.get(uuid=data['tour_operator_id'])
                user = User.objects.get(uuid=data['user_id'])

                # Verify the destination belongs to the tour operator
                if destination.tour_operator_id.uuid != touroperator.uuid:
                    return JsonResponse({"error": "Destination does not belong to the specified tour operator."}, status=403)

                # Check for duplicate destination name within the same tour operator
                # Exclude the current destination from the check
                if Destination.objects.filter(tour_operator_id__uuid=touroperator.uuid, name=data['name']).exclude(uuid=destination.uuid).exists():
                        return JsonResponse({"error": "A destination with this name already exists."}, status=409)

                # Update destination fields
                destination.name = data['name']
                destination.description = data.get('description', destination.description)
                destination.save()

                # Clear existing location mappings if locations or location_ids are provided
                if data.get('locations') or data.get('location_ids'):
                    StateCityToDestinationMapping.objects.filter(destination=destination).delete()

                locations_data = []

                # Process location_ids if provided (map existing locations)
                if data.get('location_ids'):
                    for location_id in data['location_ids']:
                        location = Location.objects.get(uuid=location_id, tour_operator=touroperator)

                        # Get or create StateCity for this location
                        statecity, _ = StateCity.objects.get_or_create(
                            state__iexact=location.state,
                            city__iexact=location.city,
                            defaults={
                                'state': location.state,
                                'city': location.city
                            }
                        )

                        # Create mapping
                        StateCityToDestinationMapping.objects.create(
                            state_city=statecity,
                            destination=destination,
                            location=location
                        )

                        locations_data.append({
                            "id": str(location.uuid),
                            "name": location.name,
                            "city": location.city,
                            "state": location.state,
                            "country": location.country,
                            "pin_code": location.pin_code,
                            "address": location.address,
                            "lng": float(location.lng) if location.lng else None,
                            "lat": float(location.lat) if location.lat else None
                        })

                # Process locations array if provided (create new or use existing)
                if data.get('locations'):
                    for location_data in data['locations']:
                        # Get or create StateCity
                        statecity, _ = StateCity.objects.get_or_create(
                            state__iexact=location_data['state'],
                            city__iexact=location_data['city'],
                            defaults={
                                'state': location_data['state'],
                                'city': location_data['city']
                            }
                        )

                        # If location_id is provided, use existing location
                        if 'location_id' in location_data and location_data['location_id']:
                            location = Location.objects.get(uuid=location_data['location_id'])
                        else:
                            # Create or get Location object with full details
                            location, created = Location.objects.get_or_create(
                                tour_operator=touroperator,
                                name=location_data.get('name', f"{location_data['city']}, {location_data['state']}"),
                                city=location_data['city'],
                                state=location_data['state'],
                                country=location_data.get('country', ''),
                                defaults={
                                    'created_by': user,
                                    'pin_code': location_data.get('pin_code'),
                                    'address': location_data.get('address'),
                                    'lng': location_data.get('lng'),
                                    'lat': location_data.get('lat')
                                }
                            )

                        # Create mapping with both StateCity and Location
                        StateCityToDestinationMapping.objects.create(
                            state_city=statecity,
                            destination=destination,
                            location=location
                        )

                        locations_data.append({
                            "id": str(location.uuid),
                            "name": location.name,
                            "city": location.city,
                            "state": location.state,
                            "country": location.country,
                            "pin_code": location.pin_code,
                            "address": location.address,
                            "lng": float(location.lng) if location.lng else None,
                            "lat": float(location.lat) if location.lat else None
                        })

                result = {
                    "id": str(destination.uuid),
                    "name": destination.name,
                    "description": destination.description,
                    "created_by_id": str(destination.created_by.uuid),
                    "tour_operator_id": str(destination.tour_operator_id.uuid),
                    "locations": locations_data,
                    "location_ids": [loc["id"] for loc in locations_data],
                    "image_ids": destination.image_ids if destination.image_ids else []
                }

                return JsonResponse(result, status=200)

        except Destination.DoesNotExist:
            return JsonResponse({"error": "Destination not found"}, status=404)
        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Location.DoesNotExist:
            return JsonResponse({"error": "Invalid location ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def get_destinations(request):
    data = json.loads(request.body.decode("utf-8"))
    destination_id = data.get('id')
    user_id = data.get('user_id')
    tour_operator_id = data.get('tour_operator_id')

    # If destination ID is provided, fetch that specific destination
    if destination_id is not None:
        try:
            destination = Destination.objects.get(uuid=destination_id)

            # Get locations for this destination
            mappings = StateCityToDestinationMapping.objects.filter(destination=destination)
            locations_data = []

            for mapping in mappings:
                if mapping.location:
                    locations_data.append({
                        "id": str(mapping.location.uuid),
                        "name": mapping.location.name,
                        "city": mapping.location.city,
                        "state": mapping.location.state,
                        "country": mapping.location.country,
                        "pin_code": mapping.location.pin_code,
                        "address": mapping.location.address,
                        "lng": float(mapping.location.lng) if mapping.location.lng else None,
                        "lat": float(mapping.location.lat) if mapping.location.lat else None
                    })

            result = {
                "id": str(destination.uuid),
                "name": destination.name,
                "description": destination.description,
                "created_by_id": str(destination.created_by.uuid),
                "tour_operator_id": str(destination.tour_operator_id.uuid),
                "locations": locations_data,
                "location_ids": [loc["id"] for loc in locations_data if "id" in loc],
                "image_ids": destination.image_ids if destination.image_ids else []
            }

            return JsonResponse(result, status=200)

        except Destination.DoesNotExist:
            return JsonResponse({"error": "Destination not found"}, status=404)

    if user_id is None and tour_operator_id is None:
        return HttpResponseBadRequest(json.dumps({
            "status": "failed",
            "code": 400,
            "message": "id, user_id, or tour_operator_id is required"
        }), content_type='application/json')

    # Filter destinations based on the provided IDs
    if user_id is not None:
        destination_queryset = Destination.objects.filter(created_by__uuid=user_id)
    elif tour_operator_id is not None:
        destination_queryset = Destination.objects.filter(tour_operator_id__uuid=tour_operator_id)
    else:
        destination_queryset = Destination.objects.all()

    # Apply pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Set page size as needed
    paginated_destinations = paginator.paginate_queryset(destination_queryset, Request(request))

    # Serialize paginated data
    result = []
    for dest in paginated_destinations:
        locations_data = []
        # Get mappings with location details
        mappings = StateCityToDestinationMapping.objects.filter(destination=dest.id).select_related('state_city', 'location')

        for mapping in mappings:
            location_info = {
                "state": mapping.state_city.state,
                "city": mapping.state_city.city
            }

            # Include full location details if available
            if mapping.location:
                location_info.update({
                    "id": str(mapping.location.uuid),
                    "name": mapping.location.name,
                    "address": mapping.location.address,
                    "pin_code": mapping.location.pin_code,
                    "country": mapping.location.country,
                    "lng": float(mapping.location.lng) if mapping.location.lng else None,
                    "lat": float(mapping.location.lat) if mapping.location.lat else None
                })

            locations_data.append(location_info)

        result.append({
            "id": str(dest.uuid),
            "name": dest.name,
            "description": dest.description,
            "created_by_id": str(dest.created_by.uuid),
            "tour_operator_id": str(dest.tour_operator_id.uuid),
            "locations": locations_data,
            "location_ids": [loc["id"] for loc in locations_data if "id" in loc],
            "image_ids": dest.image_ids if dest.image_ids else []
        })

    # Use the paginator to return paginated response
    return HttpResponse(json.dumps({
            #"status":"sucess",
            #"code":200,
            #"message": "Fetched destination records successfully",
            "data":result,
            "pagination": {
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }}), content_type='application/json')


def delete_destination(request):
    """
    Delete a destination if it's not referenced by any leads or transactions.

    Required fields:
    - destination_id: ID of the destination to delete
    - tour_operator_id: ID of the tour operator (for verification)
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    required_keys = ["destination_id", "tour_operator_id"]
    missing_keys = set(required_keys) - data.keys()

    if missing_keys:
        return JsonResponse(
            {"error": ",".join(missing_keys) + " is/are required fields."},
            status=400
        )

    destination_id = data['destination_id']
    tour_operator_id = data['tour_operator_id']

    try:
        # Get the destination and verify it belongs to the tour operator
        destination = Destination.objects.get(uuid=destination_id)

        if destination.tour_operator_id.uuid != tour_operator_id:
            return JsonResponse(
                {"error": "Destination does not belong to the specified tour operator."},
                status=403
            )

        # Check if destination is referenced by any leads
        lead_count = LeadDestinationMapping.objects.filter(destination=destination).count()
        if lead_count > 0:
            return JsonResponse(
                {
                    "error": f"Cannot delete destination. It is referenced by {lead_count} lead(s).",
                    "referenced_by": "leads",
                    "count": lead_count
                },
                status=409
            )

        # Check if destination is referenced by any transactions
        transaction_count = Transaction.objects.filter(destination=destination).count()
        if transaction_count > 0:
            return JsonResponse(
                {
                    "error": f"Cannot delete destination. It is referenced by {transaction_count} transaction(s).",
                    "referenced_by": "transactions",
                    "count": transaction_count
                },
                status=409
            )

        # If no protected references exist, delete the destination
        # This will cascade delete:
        # - StateCityToDestinationMapping entries
        # - Package entries (if any)
        # - DestinationPackageMapping entries
        # - Itineraryitem entries
        destination_name = destination.name
        destination.delete()

        return JsonResponse(
            {
                "success": f"Destination '{destination_name}' deleted successfully.",
                "deleted_id": destination_id
            },
            status=200
        )

    except Destination.DoesNotExist:
        return JsonResponse(
            {"error": "Destination not found."},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )