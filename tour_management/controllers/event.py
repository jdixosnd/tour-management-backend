from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator, Location, Event, Destination
from django.core.exceptions import ValidationError
from django.core import serializers

def add_event(request):

    required_keys = ["location", "created_by", "tour_operator", "name", "description", "contact_no","charges", "destination"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(missing_keys)+" are required fields.")

        touroperator = Touroperator.objects.filter(id = data['tour_operator'])[0]
        location = Location.objects.filter(id = data['location'])[0]
        user = User.objects.filter(id = data['created_by'])[0]
        destination = Destination.objects.filter(id = data['destination'])[0]
        event = Event(tour_operator=touroperator,
                    name=data['name'],
                    description = data['description'],
                    contact_no = data['contact_no'],
                    created_by= user,
                    destination = destination,
                    location = location,
                    charges = data['charges'])

        event.save()
        data = json.loads(serializers.serialize('json', [event],))[0]
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
            events = Event.objects.filter(tour_operator =tour_operator).filter(destination =destination)
        elif tour_operator  is not None:
            events = Event.objects.filter(tour_operator =tour_operator)
        elif destination  is not None:
            events = Event.objects.filter(destination =destination)
        else:
            raise ValidationError(
                "destination or tour_operator is required parameter.")
        
        for event in events:
            event_data = serializers.serialize('json', [event,])
            event_data = json.loads(event_data)[0]
            result.append(event_data)
    
        return HttpResponse(json.dumps(result),content_type='application/json')

