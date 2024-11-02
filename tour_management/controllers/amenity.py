from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator,Hotel, Room, Event, Cardealer, Amenity
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers

def add_amenity(request):
    required_keys = ["tour_operator_id", "created_by", "name", "type", "type_id"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(missing_keys)+" are required fields.")


        touroperator = Touroperator.objects.filter(id = data['tour_operator_id'])[0]
        user = User.objects.filter(id = data['created_by'])[0]
        if data['type'].lower() == "hotel":
            type = Hotel.objects.filter(id = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        elif data['type'].lower() == "room":
            type = Room.objects.filter(id = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        elif data['type'].lower() == "event":
            type = Event.objects.filter(id = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        elif data['type'].lower() == "cardealer":
            type = Cardealer.objects.filter(id = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        else:
            ##RAISE ERROR
            ...
        description = ""
        if "description" in data :
            if data['description'] is not None:
                description = data['description']   

        amenity = Amenity(tour_operator = touroperator,
                created_by = user,
                name = data['name'],
                type = data['type'],
                type_id = data['type_id'],
                description = description)
            
               
        amenity.save()
        data = serializers.serialize('json', [amenity,])
        return HttpResponse(data,content_type='application/json')

def get_amenities(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        type_id = None
        type = ""

        tour_operator_id  = None
        if 'tour_operator_id' in data:
            tour_operator_id = data['tour_operator_id']

        if 'cardealer_id' in data:
            type_id = data['cardealer_id']
            type="cardealer"
        elif 'hotel_id' in data:
            type_id = data['hotel_id']
            type="hotel"
        elif 'room_id' in data:
            type_id = data['room_id']
            type="room"
        elif 'event_id' in data:
            type_id = data['event_id']
            type="event"

        if tour_operator_id is not None and type_id is not None and type is not None:
            amenities = Amenity.objects.filter(tour_operator =tour_operator_id).filter(type = type).filter(type_id=type_id).all()
        
        for amenity in amenities:
            user_data = serializers.serialize('json', [amenity,])
            result.append(json.loads(user_data)[0])
        

        return HttpResponse(json.dumps(result),content_type='application/json')
