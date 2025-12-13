from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator,Hotel, Room, Event, Cardealer, Inclusion
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers

def add_inclusion(request):
    required_keys = ["tour_operator_id", "created_by", "name", "type", "type_id"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(missing_keys)+" are required fields.")


        touroperator = Touroperator.objects.filter(uuid = data['tour_operator_id'])[0]
        user = User.objects.filter(uuid = data['created_by'])[0]
        if data['type'].lower() == "hotel":
            type = Hotel.objects.filter(uuid = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        elif data['type'].lower() == "room":
            type = Room.objects.filter(uuid = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        elif data['type'].lower() == "event":
            type = Event.objects.filter(uuid = data['type_id'])
            if len(type) == 0:
                ##RAISE ERROR
                ...
        elif data['type'].lower() == "cardealer":
            type = Cardealer.objects.filter(uuid = data['type_id'])
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

        inclusion = Inclusion(tour_operator = touroperator,
                created_by = user,
                name = data['name'],
                type = data['type'],
                type_id = data['type_id'],
                description = description)
            
               
        inclusion.save()
        inclusion.save()
        data = {
            "id": str(inclusion.uuid),
            "name": inclusion.name,
            "description": inclusion.description,
            "type": inclusion.type,
            "type_id": inclusion.type_id
        }
        return HttpResponse(json.dumps([data]),content_type='application/json')

def get_inclusions(request):
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
            inclusions = Inclusion.objects.filter(tour_operator__uuid =tour_operator_id).filter(type = type).filter(type_id=type_id).all()
        
        for inclusion in inclusions:
            result.append({
                "id": str(inclusion.uuid),
                "name": inclusion.name,
                "description": inclusion.description,
                "type": inclusion.type,
                "type_id": inclusion.type_id
            })
        

        return HttpResponse(json.dumps(result),content_type='application/json')
