from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator,Destination, Location, PackageCarDealerMapping,Itineraryitem, PackageHotelMapping, Package, Event, SightSeeing, Packageitineraryitem, DestinationPackageMapping, Hotel, Cardealer, Inclusion, Exclusion
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
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
import json


def get_packages_from_destination(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        destination_id = data.get('destination_id')
        tour_operator_id = data.get('tour_operator_id')

        if not tour_operator_id:
            return JsonResponse({"error": "tour_operator_id is required."}, status=400)
        
        packages = Package.objects.filter(tour_operator_id=tour_operator_id)
        if not destination_id:
            return JsonResponse({"error": "destination_id is required."}, status=400)
        
        packages = packages.filter(tour_operator_id=tour_operator_id,destination_id=destination_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_packages = paginator.paginate_queryset(packages, Request(request))
        for package in paginated_packages:
            result.append({
                "id": package.id,
                "name": package.name,
                "destination_id":package.destination_id,
                "description": package.description,
                "pax_size": package.pax_size,
                "contains_travel_fare": package.contains_travel_fare,
                "transport_type": package.transport_type,
                "no_of_days": package.no_of_days,
                "package_amount": float(package.package_amount or 0),
                "is_active": package.is_active,
                "type": package.type
            })
        return JsonResponse({"data":result,"pagination": {
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }}, safe=False, status=200)
    
def get_package(request):
    result = []
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        destination_id = data.get('destination_id')
        tour_operator_id = data.get('tour_operator_id')
        package_id = data.get('package_id')
        
        if not tour_operator_id:
            return JsonResponse({"error": "tour_operator_id is required."}, status=400)

        # Fetch packages based on filters
        packages = Package.objects.filter(tour_operator_id=tour_operator_id)
        if destination_id:
            packages = packages.filter(destination_id=destination_id)
        if package_id:
            packages = packages.filter(id=package_id)

        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_packages = paginator.paginate_queryset(packages, Request(request))

        # Prepare each package data
        for package in paginated_packages:
            hotel_details, cardealer_details, day_wise_details = [], [], []
            itinerary_details = defaultdict(list)

            # Get destination mappings
            destinations = DestinationPackageMapping.objects.filter(package_id=package.id)
            for destination in destinations:
                #destination_details.append({
                #    "day": destination.day,
                #    "city": destination.city,
                #    "state": destination.state
                #})

                # Get only hotels mapped to this package and tour operator
                hotels_in_package = PackageHotelMapping.objects.filter(
                    package=package, tour_operator_id=tour_operator_id, hotel__location__city=destination.city
                ).select_related('hotel')

                hotel_data = {
                    "day": destination.day,
                    "city": destination.city,
                    "hotels": [get_hotel_by_id(hotel_mapping.hotel.id) for hotel_mapping in hotels_in_package]
                }
                hotel_details.append(hotel_data)

                # Get only car dealers mapped to this package and tour operator
                cardealers_in_package = PackageCarDealerMapping.objects.filter(
                    package=package, tour_operator_id=tour_operator_id, car_dealer__location__city=destination.city
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

            # Get package itinerary items
            package_itinerary_items = Packageitineraryitem.objects.filter(
                package=package.id, active=True
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
            for day, activities in itinerary_details.items():
                activities.sort(key=lambda x: x['sequence'])

                # Find matching hotel and cardealer details for each day
                hotels = next((item['hotels'] for item in hotel_details if item['day'] == day), [])
                cardealers = next((item['cardealer'] for item in cardealer_details if item['day'] == day), [])
                destionation =  next((dest for dest in destinations if dest.day == day), [])
                # Append day-wise itinerary details
                day_wise_details.append({
                    "day": day,
                    "city":destionation.city,
                    "state":destionation.state,
                    "activities": activities,
                    "hotel_details": hotels,
                    "car_dealers": cardealers
                })

            # Get inclusions and exclusions for the package
            package_inclusions = [
                {"id": inc.id, "name": inc.name, "description": inc.description}
                for inc in Inclusion.objects.filter(type="package", type_id=package.id)
            ]
            package_exclusions = [
                {"id": exc.id, "name": exc.name, "description": exc.description}
                for exc in Exclusion.objects.filter(type="package", type_id=package.id)
            ]

            # Structure final package data
            package_data = {
                "id": package.id,
                "name": package.name,
                "destination_id":package.destination_id,
                "description": package.description,
                "pax_size": package.pax_size,
                "contains_travel_fare": package.contains_travel_fare,
                "transport_type": package.transport_type,
                "no_of_days": package.no_of_days,
                "package_amount": float(package.package_amount or 0),
                "is_active": package.is_active,
                "type": package.type,
                #"destination": destination_details,
                "itinerary_details": day_wise_details,
                "inclusions": package_inclusions,
                "exclusions": package_exclusions
            }
            result.append(package_data)

        return JsonResponse({"data":result,"pagination": {
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }}, safe=False, status=200)

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
def get_city_state_from_day(data,day):
    for d in data:
        if d['day'] == day:
            return d['city'],d['state']
def add_package(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Validate required fields
        required_fields = ["tour_operator_id", "created_by", "name", "type", "destination_id", "destination_mapping", "itinerary_items"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Create Package
                tour_operator = Touroperator.objects.get(id=data['tour_operator_id'])
                created_by = User.objects.get(id=data['created_by'])
                destination = Destination.objects.get(id=data['destination_id'])
                
                package = Package.objects.create(
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
                    is_active=data.get('is_active', True)
                )

                # Add Destination mappings
                for dest in data['destination_mapping']:
                    DestinationPackageMapping.objects.create(
                        package_id=package,
                        destination_id=destination,
                        tour_operator_id=tour_operator,
                        day=dest['day'],
                        city=dest['city'],
                        state=dest['state']
                    )

                # Add Itinerary Items
                for itinerary in data['itinerary_items']:
                    day = itinerary['day']
                    
                    # Process activities within each day
                    for activity in itinerary['activities']:
                        item_type = activity['type'].lower()
                        item_name = activity['name']
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', '')
                        charges = float(activity.get('charges', 0.0))

                        # Handle Location creation or retrieval
                        location = None
                        if "location" in activity:
                            location = get_or_create_location(tour_operator, created_by, activity['location'])

                        # Create or get activity (Event or SightSeeing)
                        if item_type == "event":
                            event = get_or_create_activity(Event, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = event.id
                        elif item_type == "sightseeing":
                            sightseeing = get_or_create_activity(SightSeeing, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = sightseeing.id

                        # Create itinerary item and link to package

                        city, state=get_city_state_from_day(data['destination_mapping'],day)
                       
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

                        # Link itinerary item to package with sequence
                        Packageitineraryitem.objects.create(
                            package=package,
                            itinerary_item=itinerary_item,
                            created_by=created_by,
                            active=True,
                            is_default=True,
                            day=day,
                            sequence=activity['sequence']
                        )

                    # Map selected hotels for each day
                    for hotel_id in itinerary.get('hotel_details', []):
                        hotel = Hotel.objects.get(id=hotel_id)
                        PackageHotelMapping.objects.create(
                            package=package,
                            hotel=hotel,
                            day=day,
                            tour_operator=tour_operator,
                            selected_by=created_by
                        )

                    # Map selected car dealers for each day
                    for car_dealer_id in itinerary.get('car_dealers', []):
                        car_dealer = Cardealer.objects.get(id=car_dealer_id)
                        PackageCarDealerMapping.objects.create(
                            package=package,
                            car_dealer=car_dealer,
                            tour_operator=tour_operator,
                            day=day,
                            selected_by=created_by
                        )

                # Add inclusions and exclusions
                if "inclusions" in data:
                    for inclusion in data['inclusions']:
                        Inclusion.objects.create(
                            tour_operator=tour_operator,
                            created_by=created_by,
                            name=inclusion['name'],
                            description=inclusion.get('description', ''),
                            type="package",
                            type_id=package.id
                        )
                if "exclusions" in data:
                    for exclusion in data['exclusions']:
                        Exclusion.objects.create(
                            tour_operator=tour_operator,
                            created_by=created_by,
                            name=exclusion['name'],
                            description=exclusion.get('description', ''),
                            type="package",
                            type_id=package.id
                        )

                # Success response with package ID and summary
                return JsonResponse({
                    "message": "Package created successfully",
                    "package_id": package.id
                   
                }, status=201)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Hotel.DoesNotExist:
            return JsonResponse({"error": "One or more hotels not found"}, status=404)
        except Cardealer.DoesNotExist:
            return JsonResponse({"error": "One or more car dealers not found"}, status=404)
        except Location.DoesNotExist:
            return JsonResponse({"error": "Location data invalid or missing"}, status=404)
        except Exception as e:
            #logging.exception("An error occurred while creating the package.")
            return JsonResponse({"error": str(e)}, status=500)
        

def update_package(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Validate required fields
        required_fields = ["id", "tour_operator_id", "created_by", "name", "type", "destination_id", "destination_mapping", "itinerary_items"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Retrieve existing Package
                package = Package.objects.get(id=data['id'], tour_operator_id=data['tour_operator_id'])
                tour_operator = Touroperator.objects.get(id=data['tour_operator_id'])
                created_by = User.objects.get(id=data['created_by'])
                destination = Destination.objects.get(id=data['destination_id'])

                # Update package details
                package.name = data['name']
                package.description = data.get('description', '')
                package.type = data['type']
                package.pax_size = data.get('pax_size', None)
                package.contains_travel_fare = data.get('contains_travel_fare', False)
                package.transport_type = data.get('transport_type', '')
                package.no_of_days = data.get('no_of_days', 0)
                package.package_amount = data.get('package_amount', 0.0)
                package.notes = data.get('notes', '')
                package.is_active = data.get('is_active', True)
                package.destination = destination
                package.save()

                # Update Destination Mappings
                DestinationPackageMapping.objects.filter(package_id=package).delete()
                for dest in data['destination_mapping']:
                    DestinationPackageMapping.objects.create(
                        package_id=package,
                        destination_id=destination,
                        tour_operator_id=tour_operator,
                        day=dest['day'],
                        city=dest['city'],
                        state=dest['state']
                    )

                # Process Itinerary Items day by day
                for itinerary in data['itinerary_items']:
                    day = itinerary['day']
                    updated_items = []

                    # Process activities within each day
                    for activity in itinerary['activities']:
                        item_type = activity['type'].lower()
                        item_name = activity['name']
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', '')
                        charges = float(activity.get('charges', 0.0))

                        # Handle Location creation or retrieval
                        location = None
                        if "location" in activity:
                            location = get_or_create_location(tour_operator, created_by, activity['location'])

                        # Create or get activity (Event or SightSeeing)
                        if item_type == "event":
                            event = get_or_create_activity(Event, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = event.id
                        elif item_type == "sightseeing":
                            sightseeing = get_or_create_activity(SightSeeing, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = sightseeing.id

                        # Update or create itinerary item
                        itinerary_item, created = Itineraryitem.objects.update_or_create(
                            tour_operator_id=tour_operator,
                            created_by=created_by,
                            destination=destination,
                            city=activity.get('location', {}).get('city', ''),
                            state=activity.get('location', {}).get('state', ''),
                            item_type=item_type,
                            item_id=item_id,
                            defaults={'description': item_description}
                        )

                        # Link itinerary item to package with sequence
                        package_itinerary_item, created = Packageitineraryitem.objects.update_or_create(
                            package=package,
                            itinerary_item=itinerary_item,
                            day=day,
                            defaults={
                                'created_by': created_by,
                                'active': True,
                                'is_default': True,
                                'sequence': activity['sequence']
                            }
                        )
                        updated_items.append(package_itinerary_item.id)

                    # Remove items not in the updated_items list for the current day
                    Packageitineraryitem.objects.filter(package=package, day=day).exclude(id__in=updated_items).delete()

                    # Map selected hotels for each day
                    PackageHotelMapping.objects.filter(package=package, day=day).delete()
                    for hotel_id in itinerary.get('hotel_details', []):
                        hotel = Hotel.objects.get(id=hotel_id)
                        PackageHotelMapping.objects.create(
                            package=package,
                            hotel=hotel,
                            tour_operator=tour_operator,
                            selected_by=created_by,
                            day=day
                        )

                    # Map selected car dealers for each day
                    PackageCarDealerMapping.objects.filter(package=package, day=day).delete()
                    for car_dealer_id in itinerary.get('car_dealers', []):
                        car_dealer = Cardealer.objects.get(id=car_dealer_id)
                        PackageCarDealerMapping.objects.create(
                            package=package,
                            car_dealer=car_dealer,
                            tour_operator=tour_operator,
                            selected_by=created_by,
                            day=day
                        )

                # Update Inclusions and Exclusions
                Inclusion.objects.filter(type="package", type_id=package.id).delete()
                if "inclusions" in data:
                    for inclusion in data['inclusions']:
                        Inclusion.objects.create(
                            tour_operator=tour_operator,
                            created_by=created_by,
                            name=inclusion['name'],
                            description=inclusion.get('description', ''),
                            type="package",
                            type_id=package.id
                        )

                Exclusion.objects.filter(type="package", type_id=package.id).delete()
                if "exclusions" in data:
                    for exclusion in data['exclusions']:
                        Exclusion.objects.create(
                            tour_operator=tour_operator,
                            created_by=created_by,
                            name=exclusion['name'],
                            description=exclusion.get('description', ''),
                            type="package",
                            type_id=package.id
                        )

                # Success response with package ID and summary
                return JsonResponse({
                    "message": "Package updated successfully",
                    "package_id": package.id
                }, status=200)

        except Package.DoesNotExist:
            return JsonResponse({"error": "Package not found"}, status=404)
        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Hotel.DoesNotExist:
            return JsonResponse({"error": "One or more hotels not found"}, status=404)
        except Cardealer.DoesNotExist:
            return JsonResponse({"error": "One or more car dealers not found"}, status=404)
        except Location.DoesNotExist:
            return JsonResponse({"error": "Location data invalid or missing"}, status=404)
        except Exception as e:
            # logging.exception("An error occurred while updating the package.")
            return JsonResponse({"error": str(e)}, status=500)