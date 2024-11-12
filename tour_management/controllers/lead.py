from __future__ import unicode_literals
import json
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from collections import defaultdict
from .hotel import get_hotels_from_db, get_hotel_by_id
from .cardealer import get_transportdetails_from_db
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from collections import defaultdict
from django.db import transaction
from ..models import (
    Lead, LeadPackage, LeadDestinationMapping, LeadItineraryItem, LeadHotelMapping, 
    LeadCarDealerMapping, Customer, Touroperator, User, Destination, 
    Hotel, Cardealer, Inclusion, Exclusion, Event, SightSeeing, Location, Itineraryitem
)

def get_city_state_from_day(data,day):
    for d in data:
        if d['day'] == day:
            return d['city'],d['state']

def get_or_create_location(tour_operator, created_by, location_data):
    location = Location.objects.filter(
        tour_operator=tour_operator,
        city=location_data['city'],
        state=location_data['state'],
        name=location_data['name'],
        address=location_data['address'],
        country=location_data['country']
    ).first()
    if not location:
        location = Location.objects.create(
            tour_operator=tour_operator,
            created_by=created_by,
            city=location_data['city'],
            state=location_data['state'],
            name=location_data['name'],
            address=location_data['address'],
            country=location_data['country']
        )
    return location

def get_or_create_activity(activity_model, tour_operator, created_by, name, description, location, charges, contact_no):
    activity = activity_model.objects.filter(name=name, tour_operator=tour_operator).first()
    if not activity:
        activity = activity_model.objects.create(
            name=name,
            description=description,
            location=location,
            tour_operator=tour_operator,
            charges=charges,
            contact_no=contact_no,
            created_by=created_by
        )
    return activity

def get_lead(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body.decode("utf-8"))
            lead_package_id = data.get('lead_package_id')
            lead_package = LeadPackage.objects.get(id=lead_package_id)
            lead = Lead.objects.get(id=lead_package.lead.id)
            tour_operator_id = lead.tour_operator.id
            hotel_details, cardealer_details, day_wise_details = [], [], []
            itinerary_details = defaultdict(list)

            # Destination Mapping
            destination_mappings = LeadDestinationMapping.objects.filter(lead_package_id=lead_package)
            for destination in destination_mappings:
                #destination_details.append({
                #    "day": destination.day,
                #    "city": destination.city,
                #    "state": destination.state
                #})
                hotels_in_package = LeadHotelMapping.objects.filter(
                    lead_package=lead_package, tour_operator_id=tour_operator_id, hotel__location__city=destination.city, day = destination.day
                ).select_related('hotel')
                hotel_data = {
                    "day": destination.day,
                    "city": destination.city,
                    "hotels": [get_hotel_by_id(hotel_mapping.hotel.id) for hotel_mapping in hotels_in_package]
                }
                hotel_details.append(hotel_data)


                cardealers_in_package = LeadCarDealerMapping.objects.filter(
                    lead_package=lead_package, tour_operator_id=tour_operator_id, car_dealer__location__city=destination.city ,day = destination.day
                ).select_related('car_dealer')

                cardealer_data = {
                    "day": destination.day,
                    "city": destination.city,
                    "cardealer": [
                        {
                            "dealer_name": dealer_mapping.car_dealer.name,
                            "contact_no": dealer_mapping.car_dealer.contact_no,
                            "transport_types": get_transportdetails_from_db(dealer_mapping.car_dealer.id)
                        }
                        for dealer_mapping in cardealers_in_package
                    ]
                }
                cardealer_details.append(cardealer_data)
            
            package_itinerary_items = LeadItineraryItem.objects.filter(
                lead_package=lead_package.id
            )
            for pii in package_itinerary_items:
                itinerary = None
                if pii.itinerary_item.item_type.lower() == 'event':
                    itinerary = Event.objects.filter(id=pii.itinerary_item.item_id).first()
                elif pii.itinerary_item.item_type.lower() == 'sightseeing':
                    itinerary = SightSeeing.objects.filter(id=pii.itinerary_item.item_id).first()

                if itinerary:
                    if itinerary.location is not None:
                        location = {
                             "id": itinerary.location.id,
                            "tour_operator_id": itinerary.location.tour_operator.id,
                            "created_by_id": itinerary.location.created_by.id,
                            "city": itinerary.location.city,
                            "state": itinerary.location.state,
                            "country": itinerary.location.country,
                            "pin_code": itinerary.location.pin_code,
                            "name": itinerary.location.name,
                            "address": itinerary.location.address,
                            "lng": itinerary.location.lat,
                            "lat": itinerary.location.lng,
                        }
                    else:
                        location = {}
                    itinerary_details[pii.day].append({
                        "name": itinerary.name,
                        "type": pii.itinerary_item.item_type,
                        "description": itinerary.description,
                        "charges": float(itinerary.charges or 0),
                        "contact_no": itinerary.contact_no,
                        "sequence": pii.sequence,
                        "location": location
                    })
                # Sort itinerary details by sequence within each day
            for destination in destination_mappings:
                day = destination.day
                try:
                    activities = itinerary_details[day]
                except:
                    activities = []
                #for day, activities in itinerary_details.items():
                activities.sort(key=lambda x: x['sequence'])

                # Find matching hotel and cardealer details for each day
                hotels = next((item['hotels'] for item in hotel_details if item['day'] == day), [])
                cardealers = next((item['cardealer'] for item in cardealer_details if item['day'] == day), [])
                #destionation =  next((dest for dest in destination_mappings if dest.day == day), [])

                # Append day-wise itinerary details
                day_wise_details.append({
                    "day": day, 
                    "city":destination.city,
                    "state":destination.state,
                    "title":destination.title,
                    "description":destination.description,
                    "activities": activities,
                    "hotel_details": hotels,
                    "car_dealers": cardealers
                })
            # Get inclusions and exclusions for the package
            package_inclusions = [
                {"id": inc.id, "name": inc.name, "description": inc.description}
                for inc in Inclusion.objects.filter(type="package", type_id=lead_package.id)
            ]
            package_exclusions = [
                {"id": exc.id, "name": exc.name, "description": exc.description}
                for exc in Exclusion.objects.filter(type="package", type_id=lead_package.id)
            ]
            # Structure final package data
            lead_data = {
                "id": lead_package.id,
                "name": lead_package.name,
                "destination_id":lead_package.destination.id,
                "description": lead_package.description,
                "pax_size": lead_package.pax_size,
                "contains_travel_fare": lead_package.contains_travel_fare,
                "transport_type": lead_package.transport_type,
                "no_of_days": lead_package.no_of_days,
                "package_amount": float(lead_package.package_amount or 0),
                "type": lead_package.type,
                #"destination": destination_details,
                "itinerary_details": day_wise_details,
                "inclusions": package_inclusions,
                "exclusions": package_exclusions
            }
            
            return JsonResponse({"lead": lead_data}, status=200)

    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def add_lead(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Validate required fields
        required_fields = ["tour_operator_id", "created_by", "customer_id", "name", "type", "destination_id",  "itinerary_items"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Fetch main entities
                tour_operator = Touroperator.objects.get(id=data['tour_operator_id'])
                created_by = User.objects.get(id=data['created_by'])
                destination = Destination.objects.get(id=data['destination_id'])
                customer = Customer.objects.get(id=data['customer_id'])

                # Create the Lead record
                lead = Lead.objects.create(
                    customer=customer,
                    tour_operator=tour_operator,
                    created_by=created_by,
                    status="new"  # Assuming 'new' as the default lead status
                )

                # Create LeadPackage from provided data
                lead_package = LeadPackage.objects.create(
                    lead=lead,
                    tour_operator=tour_operator,
                    created_by=created_by,
                    name=data['name'],
                    destination=destination,
                    description=data.get('description', ''),
                    type=data['type'],
                    pax_size=data.get('pax_size', None),
                    contains_travel_fare=data.get('contains_travel_fare', False),
                    transport_type=data.get('transport_type', ''),
                    no_of_days=data.get('no_of_days', 0),
                    package_amount=data.get('package_amount', 0.0),
                    notes=data.get('notes', ''),
                )

                # Process destination mappings
                #for dest in data['destination_mapping']:
                #    LeadDestinationMapping.objects.create(
                #        lead_package=lead_package,
                #        destination=destination,
                #        tour_operator=tour_operator,
                #        day=dest['day'],
                #        city=dest['city'],
                #        state=dest['state']
                #    )

                # Process itinerary items
                for itinerary in data['itinerary_items']:
                    day = itinerary['day']
                    LeadDestinationMapping.objects.create(
                        lead_package=lead_package,
                        destination=destination,
                        tour_operator=tour_operator,
                        day=itinerary['day'],
                        city=itinerary['city'],
                        state=itinerary['state'],
                        title = itinerary['title'],
                        description = itinerary['description']

                    )
                    # Handle each activity within the day
                    for activity in itinerary['activities']:
                        item_type = activity['type'].lower()
                        item_name = activity['name']
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', '')
                        charges = float(activity.get('charges', 0.0))

                        # Location management
                        location = None
                        if "location" in activity:
                            location = get_or_create_location(tour_operator, created_by, activity['location'])

                        # Determine if it's an event or sightseeing activity
                        if item_type == "event":
                            event = get_or_create_activity(Event, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = event.id
                        elif item_type == "sightseeing":
                            sightseeing = get_or_create_activity(SightSeeing, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = sightseeing.id

                        city, state=itinerary['city'] ,itinerary['state']
                        #get_city_state_from_day(data['destination_mapping'],day)
                        itinerary_item = Itineraryitem.objects.filter(item_id=item_id, item_type=item_type,city=city,state=state,tour_operator_id=tour_operator,destination=destination).first()
                        if not itinerary_item:
                            itinerary_item = Itineraryitem.objects.create(
                                tour_operator_id=tour_operator,
                                created_by=created_by,
                                destination=destination,
                                city=city,
                                state=state,
                                item_type=item_type,
                                item_id=item_id,
                                description=item_description
                            )
                        # Create itinerary item and link to the lead package
                        lead_itinerary_item = LeadItineraryItem.objects.create(
                            lead_package=lead_package,
                            itinerary_item=itinerary_item,
                            created_by=created_by,
                            day=day,
                            sequence=activity['sequence']
                        )

                    # Map hotels of interest for each day
                    for hotel_id in itinerary.get('hotel_details', []):
                        hotel = Hotel.objects.get(id=hotel_id)
                        LeadHotelMapping.objects.create(
                            lead_package=lead_package,
                            hotel=hotel,
                            day=day,
                            tour_operator=tour_operator,
                            selected_by=created_by
                        )

                    # Map car dealers of interest for each day
                    for car_dealer_id in itinerary.get('car_dealers', []):
                        car_dealer = Cardealer.objects.get(id=car_dealer_id)
                        LeadCarDealerMapping.objects.create(
                            lead_package=lead_package,
                            car_dealer=car_dealer,
                            tour_operator=tour_operator,
                            day=day,
                            selected_by=created_by
                        )

                # Add package inclusions and exclusions to the lead
                #if "inclusions" in data:
                #    for inclusion in data['inclusions']:
                #        Inclusion.objects.create(
                #            tour_operator=tour_operator,
                #            created_by=created_by,
                #            name=inclusion['name'],
                #            description=inclusion.get('description', ''),
                #            type="lead_package",
                #            type_id=lead_package.id
                #        )
                #if "exclusions" in data:
                #    for exclusion in data['exclusions']:
                #        Exclusion.objects.create(
                #            tour_operator=tour_operator,
                #            created_by=created_by,
                #            name=exclusion['name'],
                #            description=exclusion.get('description', ''),
                #            type="lead_package",
                #            type_id=lead_package.id
                #        )

                # Response after successful lead creation
                return JsonResponse({
                    "message": "Lead created successfully",
                    "lead_id": lead.id
                }, status=201)

        except (Touroperator.DoesNotExist, User.DoesNotExist, Customer.DoesNotExist):
            return JsonResponse({"error": "Invalid ID for tour operator, user, or customer"}, status=400)
        except (Hotel.DoesNotExist, Cardealer.DoesNotExist):
            return JsonResponse({"error": "One or more hotels or car dealers not found"}, status=404)
        except Location.DoesNotExist:
            return JsonResponse({"error": "Location data invalid or missing"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)