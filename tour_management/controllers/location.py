from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import Location, Touroperator, User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist


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
        id=data['tour_operator_id'])[0]

    user = User.objects.filter(
        id=data['user_id'])[0]

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
    data = json.loads(serializers.serialize('json', [location,]))
    return {
            "code":200,
            "data": data
        }

def add_location(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        resp = add_location_to_db(data)
        if resp['code'] == 400:
            return HttpResponseBadRequest(json.dumps({"error": resp['error'] }), content_type='application/json')
        else:
            HttpResponse(resp['data'], content_type='application/json')


def update_location_in_db(data):
    required_keys = ["id", "tour_operator_id","created_by_id",
                     "name", "city", "state", "country"]
    missing_keys = set(required_keys) - data.keys()

    # Check for missing keys
    if missing_keys:
        return {"code":400, "error": ",".join(missing_keys) + " is/are required fields."}

    location = Location.objects.filter(
        id=data['id'], tour_operator=data['tour_operator_id']).first()
    if location is None:
        return {"code":400, "error": "Location for given tour_operator_id doesnt exist."}

        #return HttpResponseBadRequest(json.dumps({"error": "Location for given tour_operator_id doesnt exist."}), content_type='application/json')

    touroperator = Touroperator.objects.filter(
        id=data['tour_operator_id']).first()
    user = User.objects.filter(id=data['created_by_id']).first()

    # Check if another location with the same name, city, state, and country exists
    if Location.objects.filter(
        tour_operator=touroperator.id,
        city=data['city'],
        state=data['state'],
        country=data['country'],
        name=data['name']
    ).exclude(id=data['id']).exists():
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
        "id": location.id,
        "tour_operator_id": location.tour_operator.id,
        "created_by_id": location.created_by.id,
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
        resp = json.loads(request.body.decode("utf-8"))
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

        location = Location.objects.filter(tour_operator_id=tour_operator_id)

        locations = []
        for loc in location:
            locations.append({
                "id": loc.id,
                "tour_operator_id": loc.tour_operator.id,
                "created_by_id": loc.created_by.id,
                "city": loc.city,
                "state": loc.state,
                "country": loc.country,
                "pin_code": loc.pin_code,
                "name": loc.name,
                "address": loc.address,
                "lng": float(loc.lng),
                "lat": float(loc.lat),
                "created_at": str(loc.created_at)
            })

        return HttpResponse(json.dumps(locations), content_type='application/json')

def delete_location(request):
    data = json.loads(request.body.decode("utf-8"))
    required_keys = ["location_id", "tour_operator_id"]
    missing_keys = set(required_keys) - data.keys()

    if missing_keys:
            return HttpResponseBadRequest(json.dumps({"error": ",".join(missing_keys) + " is/are required fields."}), content_type='application/json')
    location_id = data['location_id']
    tour_operator_id = data['tour_operator_id']

    try:
        location = Location.objects.get(id=location_id, tour_operator_id=tour_operator_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({"error": "Location not found or doesn't belong to the specified tour operator."}), content_type='application/json')

    # Delete the location
    location.delete()
    return HttpResponse(json.dumps({"success": "Location deleted successfully."}), content_type='application/json')