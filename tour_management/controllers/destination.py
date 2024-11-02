from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import Destination, StateCityToDestinationMapping,StateCity,Touroperator, User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request


def add_destination(request):
    required_keys = ["tour_operator_id", "user_id",
                     "name","locations"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(required_keys) + " are required fields.")

        touroperator = Touroperator.objects.filter(
            id=data['tour_operator_id'])[0]
        
        user = User.objects.filter(
            id = data['user_id'])[0]
        

        if Destination.objects.filter(tour_operator_id=touroperator).filter(name=data['name']).exists():
            return HttpResponseBadRequest(json.dumps({"Error": "The destination already exists."}), content_type='application/json')

        
        destination = Destination(tour_operator_id=touroperator,
                    created_by=user,
                    name=data['name'],
                    description=data['description'])
        destination.save()

        for location in data['locations']:
            statecity = StateCity.objects.filter(state__iexact = location['state']).filter(city__iexact=location['city']).first()
                
            scd =StateCityToDestinationMapping(state_city = statecity,destination = destination)
            scd.save()
        
        data = serializers.serialize('json', [destination,])
        return HttpResponse(data, content_type='application/json')


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

def get_destinations(request):
    data = json.loads(request.body.decode("utf-8"))
    user_id = data.get('user_id')
    tour_operator_id = data.get('tour_operator_id')

    if user_id is None and tour_operator_id is None:
        return HttpResponseBadRequest(json.dumps({
            "status": "failed",
            "code": 400,
            "message": "User_id or tour_operator_id is required"
        }), content_type='application/json')

    # Filter destinations based on the provided IDs
    if user_id is not None:
        destination_queryset = Destination.objects.filter(id=user_id)
    elif tour_operator_id is not None:
        destination_queryset = Destination.objects.filter(tour_operator_id=tour_operator_id)
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
        locations = StateCityToDestinationMapping.objects.filter(destination=dest.id).all()
        for loc in locations:
            location = StateCity.objects.filter(id = loc.state_city_id).first()
            locations_data.append({"state":location.state,"city":location.city})
        result.append({
            "id": dest.id,
            "name": dest.name,
            "description": dest.description,
            "created_by_id": dest.created_by.id,
            "tour_operator_id": dest.tour_operator_id.id,
            "locations":locations_data
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