from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator, Location, Event, Destination
from django.core.exceptions import ValidationError
from django.core import serializers

def add_event(request):

    required_keys = ["location", "created_by", "tour_operator", "name", "description", "destination"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(missing_keys)+" are required fields.")

        touroperator = Touroperator.objects.filter(uuid = data['tour_operator'])[0]
        location = Location.objects.filter(uuid = data['location'])[0]
        user = User.objects.filter(uuid = data['created_by'])[0]
        destination = Destination.objects.filter(uuid = data['destination'])[0]
        event = Event(tour_operator=touroperator,
                    name=data['name'],
                    description = data['description'],
                    contact_no = data.get('contact_no'),
                    created_by= user,
                    destination = destination,
                    location = location,
                    charges = data.get('charges'))

        event.save()
        event.save()
        data = {
            "id": str(event.uuid),
            "name": event.name,
            "description": event.description,
            "tour_operator": str(event.tour_operator.uuid),
            "location": str(event.location.uuid),
            "created_by": str(event.created_by.uuid),
            "destination": str(event.destination.uuid),
            "charges": event.charges,
            "contact_no": event.contact_no
        }
        return HttpResponse(json.dumps(data),content_type='application/json')


def get_events(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        destination = None
        tour_operator  = None
        if 'destination' in data:
            destination = data['destination']
        
        if 'tour_operator' in data:
            tour_operator = data['tour_operator']

        if destination is not None and tour_operator is not None:
            events = Event.objects.filter(tour_operator__uuid =tour_operator).filter(destination__uuid =destination)
        elif tour_operator  is not None:
            events = Event.objects.filter(tour_operator__uuid =tour_operator)
        elif destination  is not None:
            events = Event.objects.filter(destination__uuid =destination)
        else:
            raise ValidationError(
                "destination or tour_operator is required parameter.")
        
        for event in events:
            event_data = {
                "id": str(event.uuid),
                "name": event.name,
                "description": event.description,
                "tour_operator": str(event.tour_operator.uuid),
                "location": str(event.location.uuid),
                "created_by": str(event.created_by.uuid),
                "destination": str(event.destination.uuid),
                "charges": event.charges,
                "contact_no": event.contact_no
            }
            result.append(event_data)
    
        return HttpResponse(json.dumps(result),content_type='application/json')

