from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import json
from ..models import Location, Touroperator, User, Cardealer, Hotel, Event, SightSeeing
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError


def add_location_to_db(data):
    required_keys = ["tour_operator_id", "user_id",
                     "name", "city", "state", "country"]
    missing_keys = set(required_keys) - data.keys()
    if missing_keys:
        return {
            "code":400,
            "error": ",".join(required_keys) + " is/are required fields."
        }

    touroperator = Touroperator.objects.filter(
        uuid=data['tour_operator_id'])[0]

    user = User.objects.filter(
        uuid=data['user_id'])[0]

    if Location.objects.filter(tour_operator=touroperator).filter(city=data['city']).filter(state=data['state']).filter(country=data['country']).filter(name=data['name']).exists():
        return {
            "code":400,
            "error": "The location already exists."
        }

    location = Location(tour_operator=touroperator,
                        created_by=user,
                        city=data['city'],
                        state=data['state'],
                        country=data['country'],
                        pin_code=data['pin_code'] if 'pin_code' in data else '',
                        name=data['name'],
                        address=data['address'] if 'address' in data else '',
                        lat=data['lat'] if 'lat' in data else None,
                        lng=data['lng'] if 'lng' in data else None)

    location.save()
    data = {"tour_operator": str(location.tour_operator.uuid),
            "created_by": str(location.created_by.uuid),
            "city": location.city,
            "state": location.state,
            "country": location.country,
            "pin_code": location.pin_code,
            "name": location.name,
            "address": location.address,
            "lng": location.get_lng_float(),
            "lat": location.get_lat_float()}
    return {
            "code":200,
            "data": data,
            "id": str(location.uuid)
        }

def add_location(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        resp = add_location_to_db(data)
        if resp['code'] == 400:
            return HttpResponseBadRequest(json.dumps({"error": resp['error'] }), content_type='application/json')
        else:
            return HttpResponse(json.dumps(resp['data']), content_type='application/json')


def update_location_in_db(data):
    required_keys = ["id", "tour_operator_id","created_by_id",
                     "name", "city", "state", "country"]
    missing_keys = set(required_keys) - data.keys()

    # Check for missing keys
    if missing_keys:
        return {"code":400, "error": ",".join(missing_keys) + " is/are required fields."}

    location = Location.objects.filter(
        uuid=data['id'], tour_operator__uuid=data['tour_operator_id']).first()
    if location is None:
        return {"code":400, "error": "Location for given tour_operator_id doesnt exist."}

        #return HttpResponseBadRequest(json.dumps({"error": "Location for given tour_operator_id doesnt exist."}), content_type='application/json')

    touroperator = Touroperator.objects.filter(
        uuid=data['tour_operator_id']).first()
    user = User.objects.filter(uuid=data['created_by_id']).first()

    # Check if another location with the same name, city, state, and country exists
    if Location.objects.filter(
        tour_operator=touroperator.id,
        city=data['city'],
        state=data['state'],
        country=data['country'],
        name=data['name']
    ).exclude(uuid=data['id']).exists():
        return {"code":422, "error": "A location with these details already exists."}
        #return HttpResponseBadRequest(json.dumps({"error": "A location with these details already exists."}), content_type='application/json')

    # Update location fields
    if 'user_id' in data:
        location.created_by = user
    if 'name' in data:
        location.name = data['name']
    if 'city' in data:
        location.city = data['city']
    if 'state' in data:
        location.state = data['state']
    if 'country' in data:
        location.country = data['country']
    if 'pin_code' in data:
        location.pin_code = data.get(
            'pin_code', location.pin_code)
    if 'address' in data:
        location.address = data.get('address', location.address)
    if 'lat' in data:
        location.lat = data.get('lat', location.lat)
    if 'lng' in data:
        location.lng = data.get('lng', location.lng)

    location.save()

    loc = {
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
    }
    return {"code":200, "data":loc}

def update_location(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        resp = update_location_in_db(data)
        if resp['code'] == 200:
            return HttpResponse(json.dumps(resp['data']), content_type='application/json')
        else:
            return  HttpResponseBadRequest(json.dumps({"error": resp['error']}), content_type='application/json')

def get_locations(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        tour_operator_id = None

        if 'tour_operator_id' in data:
            tour_operator_id = data['tour_operator_id']

        if tour_operator_id is None:
            return HttpResponseBadRequest(json.dumps({"error": "tour_operator_id is required field"}), content_type='application/json')

        location = Location.objects.filter(tour_operator__uuid=tour_operator_id)

        locations = []
        for loc in location:
            locations.append({
                "id": str(loc.uuid),
                "tour_operator_id": str(loc.tour_operator.uuid),
                "created_by_id": str(loc.created_by.uuid),
                "city": loc.city,
                "state": loc.state,
                "country": loc.country,
                "pin_code": loc.pin_code,
                "name": loc.name,
                "address": loc.address,
                "lng": loc.get_lng_float(),
                "lat": loc.get_lat_float(),
                "created_at": str(loc.created_at)
            })

        return HttpResponse(json.dumps(locations), content_type='application/json')

def delete_location(request):
    """
    Delete a location if it's not referenced by any protected resources.

    Required fields:
    - location_id: ID of the location to delete
    - tour_operator_id: ID of the tour operator (for verification)
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    required_keys = ["location_id", "tour_operator_id"]
    missing_keys = set(required_keys) - data.keys()

    if missing_keys:
        return JsonResponse(
            {"error": ",".join(missing_keys) + " is/are required fields."},
            status=400
        )

    location_id = data['location_id']
    tour_operator_id = data['tour_operator_id']

    try:
        # Get the location and verify it belongs to the tour operator
        location = Location.objects.get(uuid=location_id, tour_operator__uuid=tour_operator_id)
        location_name = location.name

        # Check if location is used by any hotels
        hotels_count = Hotel.objects.filter(location=location).count()

        # Check if location is used by any car dealers
        cardealers_count = Cardealer.objects.filter(location=location).count()

        # Check if location is used by any events
        events_count = Event.objects.filter(location=location).count()

        # Check if location is used by any sightseeing
        sightseeing_count = SightSeeing.objects.filter(location=location).count()

        # Build list of references
        references = []
        if hotels_count > 0:
            references.append(f"{hotels_count} hotel(s)")
        if cardealers_count > 0:
            references.append(f"{cardealers_count} car dealer(s)")
        if events_count > 0:
            references.append(f"{events_count} event(s)")
        if sightseeing_count > 0:
            references.append(f"{sightseeing_count} sightseeing(s)")

        # If there are references, check if they're used in leads/transactions
        if references:
            return JsonResponse(
                {
                    "error": f"Cannot delete location. It is used by {', '.join(references)}. These may be referenced in leads or transactions.",
                    "details": {
                        "hotels": hotels_count,
                        "car_dealers": cardealers_count,
                        "events": events_count,
                        "sightseeing": sightseeing_count
                    }
                },
                status=409
            )

        # If no references, delete the location
        location.delete()

        return JsonResponse(
            {
                "success": f"Location '{location_name}' deleted successfully.",
                "deleted_id": location_id
            },
            status=200
        )

    except ObjectDoesNotExist:
        return JsonResponse(
            {"error": "Location not found or doesn't belong to the specified tour operator."},
            status=404
        )
    except ProtectedError as e:
        # This shouldn't happen if we check properly above, but just in case
        return JsonResponse(
            {
                "error": "Cannot delete location because it is referenced by other records (leads or transactions).",
                "details": str(e)
            },
            status=409
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )