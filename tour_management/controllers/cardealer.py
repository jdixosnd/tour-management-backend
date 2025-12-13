from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import Location, Touroperator, User, Cardealer, CarType, Destination, StateCityToDestinationMapping, StateCity, LeadCarDealerMapping, PackageCarDealerMapping
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core import serializers
from .location import add_location_to_db, update_location_in_db
from django.http import JsonResponse
from django.db import transaction

def get_transportdetails_from_db(id):
    cartypes = []
    cartypes_from_db = CarType.objects.filter(car_dealer_id=id).all()
    for cartype in cartypes_from_db:
        cartypes.append({"name": cartype.name, "type": cartype.type})
    return cartypes


def add_cardealer(request):
    required_keys = ["tour_operator_id", "location", "created_by_id", "name", "cartypes"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        if missing_keys:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_keys)}"}, status=400)

        try:
            with transaction.atomic():
                # Fetch tour operator and user
                touroperator = Touroperator.objects.get(uuid=data['tour_operator_id'])
                user = User.objects.get(uuid=data['created_by_id'])
                
                # Check if CarDealer with the same contact_no exists for this tour operator
                if Cardealer.objects.filter(tour_operator=touroperator, contact_no=data['contact_no']).exists():
                    return JsonResponse({"error": "A Car Dealer with this contact number already exists."}, status=409)

                # Check for existing location or create a new one
                location_data = data['location']
                location, created = Location.objects.get_or_create(
                    tour_operator=touroperator,
                    name=location_data['name'],
                    city=location_data['city'],
                    state=location_data['state'],
                    country=location_data['country'],
                    defaults={
                        'created_by': user,
                        'pin_code': location_data.get('pin_code'),
                        'address': location_data.get('address'),
                        'lng': location_data.get('lng'),
                        'lat': location_data.get('lat')
                    }
                )

                # Create Car Dealer entry
                cardealer = Cardealer.objects.create(
                    tour_operator=touroperator,
                    created_by=user,
                    location=location,
                    name=data['name'],
                    contact_no=data.get('contact_no')
                )

                # Create Car Types
                cartypes_data = data['cartypes']
                cartypes = []
                for cartype_data in cartypes_data:
                    cartype = CarType.objects.create(
                        tour_operator=touroperator,
                        car_dealer=cardealer,
                        name=cartype_data['name'],
                        type=cartype_data['type'],
                        capacity=cartype_data['capacity']
                    )
                    cartypes.append({
                        "id": str(cartype.uuid),
                        "name": cartype.name,
                        "type": cartype.type,
                        "capacity": cartype.capacity,
                        "created_at": str(cartype.created_at)
                    })

                # Prepare result
                result = {
                    "id": str(cardealer.uuid),
                    "tour_operator_id": str(cardealer.tour_operator.uuid),
                    "created_by": str(cardealer.created_by.uuid),
                    "name": cardealer.name,
                    "contact_no": cardealer.contact_no,
                    "location": {
                        "id": str(location.uuid),
                        "city": location.city,
                        "state": location.state,
                        "country": location.country,
                        "pin_code": location.pin_code,
                        "name": location.name,
                        "address": location.address,
                        "lng": float(location.lng),
                        "lat": float(location.lat)
                    },
                    "cartypes": cartypes
                }

            # Return success response
            return JsonResponse(result, status=201)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Exception as e:
            # Any unexpected errors trigger a rollback and return a general error response
            return JsonResponse({"error": str(e)}, status=500)
        
def update_cardealer(request):
    required_keys = ["id", "tour_operator_id", "location", "created_by_id", "name", "contact_no"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        if missing_keys:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_keys)}"}, status=400)

        try:
            with transaction.atomic():
                # Fetch car dealer and tour operator
                cardealer = Cardealer.objects.select_related('location').filter(
                    uuid=data['id'], tour_operator__uuid=data['tour_operator_id']
                ).first()
                
                if cardealer is None:
                    return JsonResponse({"error": "Car dealer with the given ID does not exist."}, status=404)

                # Update or reuse existing location
                location_data = data['location']
                location, created = Location.objects.get_or_create(
                    tour_operator__uuid=data['tour_operator_id'],
                    name=location_data['name'],
                    city=location_data['city'],
                    state=location_data['state'],
                    country=location_data['country'],
                    defaults={
                        # 'created_by_id': data['created_by_id'] # Use user object from lookup
                        'created_by': User.objects.get(uuid=data['created_by_id'])
                    }
                )
                
                # If location already exists, update the existing one if necessary
                #if not created:
                location.pin_code = location_data.get('pin_code', location.pin_code)
                location.address = location_data.get('address', location.address)
                location.lng = location_data.get('lng', location.lng)
                location.lat = location_data.get('lat', location.lat)
                location.save()

                # Update Car Dealer details
                cardealer.location = location
                cardealer.name = data['name']
                cardealer.contact_no = data.get('contact_no', cardealer.contact_no)
                cardealer.save()

                # Update Car Types
                cartypes_data = data.get('cartypes', [])
                if not cartypes_data:
                    # Delete all Car Types if 'cartypes' in request is empty
                    CarType.objects.filter(car_dealer=cardealer).delete()
                else:
                    # Update or add Car Types
                    existing_cartype_ids = set()
                    for cartype_data in cartypes_data:
                        cartype_id = cartype_data.get('id')
                        if cartype_id:
                            # Update existing Car Type if it exists
                            cartype = CarType.objects.filter(uuid=cartype_id, car_dealer=cardealer).first()
                            if cartype:
                                cartype.name = cartype_data['name']
                                cartype.type = cartype_data['type']
                                cartype.capacity = cartype_data['capacity']
                                cartype.save()
                                existing_cartype_ids.add(cartype_id)
                            else:
                                # If the ID doesn't exist, create a new Car Type
                                new_cartype = CarType.objects.create(
                                    tour_operator=cardealer.tour_operator,
                                    car_dealer=cardealer,
                                    name=cartype_data['name'],
                                    type=cartype_data['type'],
                                    capacity=cartype_data['capacity']
                                )
                                existing_cartype_ids.add(new_cartype.uuid)
                        else:
                            # Create new Car Type if no ID is provided
                            new_cartype = CarType.objects.create(
                                tour_operator=cardealer.tour_operator,
                                car_dealer=cardealer,
                                name=cartype_data['name'],
                                type=cartype_data['type'],
                                capacity=cartype_data['capacity']
                            )
                            existing_cartype_ids.add(new_cartype.uuid)

                    # Delete any Car Types that are not in the updated list
                    CarType.objects.filter(car_dealer=cardealer).exclude(uuid__in=existing_cartype_ids).delete()

                # Prepare the response data
                updated_cartypes = [{"id": str(c.uuid), "name": c.name, "type": c.type, "capacity": c.capacity, "created_at": c.created_at} for c in CarType.objects.filter(car_dealer=cardealer)]
                
                cardealer_obj = {
                    "id": str(cardealer.uuid),
                    "tour_operator_id": str(cardealer.tour_operator.uuid),
                    "created_by_id": str(cardealer.created_by.uuid),
                    "name": cardealer.name,
                    "contact_no": cardealer.contact_no,
                    "location": {
                        "id": str(location.uuid),
                        "tour_operator_id": str(location.tour_operator.uuid),
                        "created_by_id": str(location.created_by.uuid),
                        "city": location.city,
                        "state": location.state,
                        "country": location.country,
                        "pin_code": location.pin_code,
                        "name": location.name,
                        "address": location.address,
                        "lng": float(location.lng),
                        "lat": float(location.lat),
                        "created_at": str(location.created_at)
                    },
                    "cartypes": updated_cartypes
                }
                
            # Return success response
            return JsonResponse(cardealer_obj, status=200)

        except Exception as e:
            # Any unexpected errors trigger a rollback and return a general error response
            return JsonResponse({"error": str(e)}, status=500)

def add_car_type_for_cardealer(request):
    required_keys = ["tour_operator_id", "car_dealer",
                     "name", "type", "capacity", "created_by"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(required_keys) + " are required fields.")
        touroperator = Touroperator.objects.filter(
            uuid=data['tour_operator_id'])[0]

        cardealer = Cardealer.objects.filter(
            uuid=data['car_dealer'])[0]

        cartype = CarType(tour_operator=touroperator,
                          car_dealer=cardealer,
                          name=data['name'],
                          type=data['type'],
                          capacity=data['capacity'])
        cartype.save()
        data = serializers.serialize('json', [cartype,])
        return JsonResponse(data, safe=False)
 
def fetch_car_types(cardealer_id):
    cartypes = CarType.objects.filter(car_dealer__uuid=cardealer_id).all()
    return [{"id": str(c.uuid), "name": c.name, "type": c.type, "capacity": c.capacity} for c in cartypes]

def get_cardealer(request):
    result = []
    required_keys = ["tour_operator_id" ]


    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            return HttpResponseBadRequest(json.dumps({"error": ",".join(required_keys) + " is/are required fields."}), content_type='application/json')


        cardealer_id = data.get('cardealer_id')
        tour_operator_id = data.get('tour_operator_id')
        destination_id = data.get('destination_id')

        # Fetch with select_related for optimization
        if cardealer_id:
            cardealers = Cardealer.objects.filter(uuid=cardealer_id).select_related('tour_operator', 'created_by', 'location')
        elif tour_operator_id:
            cardealers = Cardealer.objects.filter(tour_operator__uuid=tour_operator_id).select_related('tour_operator', 'created_by', 'location')

        # Filter by destination if destination_id is provided
        if destination_id:
            try:
                # Get the destination
                destination = Destination.objects.get(uuid=destination_id)

                # Get all location mappings for this destination
                destination_mappings = StateCityToDestinationMapping.objects.filter(
                    destination=destination
                ).select_related('state_city', 'location')

                # Collect location IDs and city/state combinations
                location_ids = []
                city_state_filters = []

                for mapping in destination_mappings:
                    # If mapping has a direct location reference, use it
                    if mapping.location:
                        location_ids.append(mapping.location.uuid)
                    else:
                        # Fallback to city/state matching for old data
                        city_state_filters.append({
                            'city__iexact': mapping.state_city.city,
                            'state__iexact': mapping.state_city.state
                        })

                # Build query to filter cardealers
                if location_ids or city_state_filters:
                    from django.db.models import Q
                    location_query = Q()

                    # Add direct location ID matches
                    if location_ids:
                        location_query |= Q(location__uuid__in=location_ids)

                    # Add city/state matches for backward compatibility
                    if city_state_filters:
                        for loc_filter in city_state_filters:
                            location_query |= Q(location__city__iexact=loc_filter['city__iexact'],
                                              location__state__iexact=loc_filter['state__iexact'])

                    # Filter cardealers by matching locations
                    cardealers = cardealers.filter(location_query)
                else:
                    # No locations found for this destination, return empty result
                    cardealers = Cardealer.objects.none()

            except Destination.DoesNotExist:
                return JsonResponse({"error": "Invalid destination ID"}, status=400)

        for dealer in cardealers:
            dealer_data = {
                "id": str(dealer.uuid),
                "tour_operator_id": str(dealer.tour_operator.uuid),
                "created_by_id": str(dealer.created_by.uuid),
                "name": dealer.name,
                "contact_no": dealer.contact_no,
                "created_at": str(dealer.created_at),
                "location": {
                    "id": str(dealer.location.uuid),
                    "tour_operator_id": str(dealer.location.tour_operator.uuid),
                    "created_by_id": str(dealer.location.created_by.uuid),
                    "city": dealer.location.city,
                    "state": dealer.location.state,
                    "country": dealer.location.country,
                    "pin_code": dealer.location.pin_code,
                    "name": dealer.location.name,
                    "address": dealer.location.address,
                    "lng": float(dealer.location.lng),
                    "lat": float(dealer.location.lat),
                    "created_at": str(dealer.location.created_at)
                }
            }
            dealer_data['cartypes'] = fetch_car_types(dealer_data['id'])
            result.append(dealer_data)

        return JsonResponse(result, safe=False)


def delete_cardealer(request):
    """
    Delete a car dealer if it's not referenced by any leads or packages.

    Required fields:
    - id: ID of the car dealer to delete
    - tour_operator_id: ID of the tour operator (for verification)
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    required_keys = ["id", "tour_operator_id"]
    missing_keys = set(required_keys) - data.keys()

    if missing_keys:
        return JsonResponse(
            {"error": ",".join(missing_keys) + " is/are required fields."},
            status=400
        )

    cardealer_id = data['id']
    tour_operator_id = data['tour_operator_id']

    try:
        # Get the car dealer and verify it belongs to the tour operator
        cardealer = Cardealer.objects.get(uuid=cardealer_id)

        if cardealer.tour_operator.uuid != tour_operator_id:
            return JsonResponse(
                {"error": "Car dealer does not belong to the specified tour operator."},
                status=403
            )

        # Check if car dealer is referenced by any leads
        lead_count = LeadCarDealerMapping.objects.filter(car_dealer=cardealer).count()
        if lead_count > 0:
            return JsonResponse(
                {
                    "error": f"Cannot delete car dealer. It is referenced by {lead_count} lead(s).",
                    "referenced_by": "leads",
                    "count": lead_count
                },
                status=409
            )

        # Check if car dealer is referenced by any packages
        package_count = PackageCarDealerMapping.objects.filter(car_dealer=cardealer).count()
        if package_count > 0:
            return JsonResponse(
                {
                    "error": f"Cannot delete car dealer. It is referenced by {package_count} package(s).",
                    "referenced_by": "packages",
                    "count": package_count
                },
                status=409
            )

        # If no protected references exist, delete the car dealer
        # This will cascade delete:
        # - CarType entries associated with this car dealer
        cardealer_name = cardealer.name
        cardealer.delete()

        return JsonResponse(
            {
                "success": f"Car dealer '{cardealer_name}' deleted successfully.",
                "deleted_id": cardealer_id
            },
            status=200
        )

    except Cardealer.DoesNotExist:
        return JsonResponse(
            {"error": "Car dealer not found."},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )
