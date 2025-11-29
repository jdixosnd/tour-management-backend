from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator,Destination, Location, PackageCarDealerMapping,Itineraryitem, PackageHotelMapping, Package, Event, SightSeeing, Packageitineraryitem, DestinationPackageMapping, Hotel, Cardealer, QuickHotel, Inclusion, Exclusion, ImageMetadata, PackageOption, PackageOptionHotelMapping, PackageOptionCarDealerMapping, Room, StateCityToDestinationMapping
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from collections import defaultdict
from .hotel import get_hotels_from_db, get_hotel_by_id, get_images
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
        
        packages = Package.objects.filter(tour_operator_id=tour_operator_id).order_by('-updated_at')
        if not destination_id:
            return JsonResponse({"error": "destination_id is required."}, status=400)
        
        packages = packages.filter(tour_operator_id=tour_operator_id,destination_id=destination_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_packages = paginator.paginate_queryset(packages, Request(request))
        for package in paginated_packages:
            # Get package images
            package_images = get_images('package', package.id, include_binary=False)

            # Get package options with hotel mappings
            package_options_data = []
            package_options = PackageOption.objects.filter(package=package).order_by('id')
            for option in package_options:
                # Get hotel mappings for this option, grouped by day
                hotel_mappings_data = []
                hotel_mappings = PackageOptionHotelMapping.objects.filter(
                    package_option=option
                ).select_related('hotel').order_by('day')

                # Group hotels by day
                day_hotel_map = defaultdict(list)
                for mapping in hotel_mappings:
                    day_hotel_map[mapping.day].append(mapping.hotel.id)

                # Convert to the required format
                for day, hotel_ids in sorted(day_hotel_map.items()):
                    hotel_mappings_data.append({
                        "day": day,
                        "hotel_ids": hotel_ids
                    })

                package_options_data.append({
                    "id": option.id,
                    "name": option.name,
                    "amount": float(option.amount),
                    "description": option.description,
                    "hotel_mappings": hotel_mappings_data
                })

            result.append({
                "id": package.id,
                "created_at": package.created_at.isoformat() if package.created_at else None,
                "updated_at": package.updated_at.isoformat() if package.updated_at else None,
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
                "terms_and_conditions": package.terms_and_conditions,
                "images": package_images,
                "package_options": package_options_data
            })
        return JsonResponse({"data":result,"pagination": {
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            }}, safe=False, status=200)
    
def get_all_packages(request):
    """
    Lightweight package listing API for card/list views.

    Request body:
    {
        "tour_operator_id": 1,          # required
        "destination_id": 2,            # optional filter
        "page": 1,                      # optional
        "page_size": 20                 # optional, defaults to no pagination when omitted
    }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)

    tour_operator_id = data.get('tour_operator_id')
    destination_id = data.get('destination_id')

    # Optional pagination from request body
    page = data.get('page')
    page_size = data.get('page_size')

    if not tour_operator_id:
        return JsonResponse({"error": "tour_operator_id is required."}, status=400)

    try:
        packages = Package.objects.filter(tour_operator_id=tour_operator_id)
        if destination_id:
            packages = packages.filter(destination_id=destination_id)
        packages = packages.order_by('-updated_at')

        # Apply manual pagination only when page is provided
        pagination = None
        if page is not None:
            try:
                page = int(page)
                page_size = int(page_size) if page_size is not None else 10
            except (TypeError, ValueError):
                return JsonResponse({"error": "page and page_size must be integers."}, status=400)

            if page <= 0 or page_size <= 0:
                return JsonResponse({"error": "page and page_size must be positive integers."}, status=400)

            total_count = packages.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            packages = packages[start_index:end_index]
            pagination = {
                "count": total_count,
                "num_pages": (total_count + page_size - 1) // page_size,
                "current_page": page,
                "page_size": page_size
            }

        packages_data = []
        for package in packages:
            package_images = get_images('package', package.id, include_binary=False)
            images = [
                {
                    "id": image.get("id"),
                    "url": image.get("image_url")
                }
                for image in package_images
                if image.get("id") is not None and image.get("image_url") is not None
            ]

            # Build destination location list
            locations = []
            seen_locations = set()
            if package.destination:
                mappings = StateCityToDestinationMapping.objects.filter(
                    destination=package.destination
                ).select_related('state_city', 'location')

                for mapping in mappings:
                    city = mapping.state_city.city if mapping.state_city else None
                    state = mapping.state_city.state if mapping.state_city else None
                    country = mapping.location.country if mapping.location else ""
                    key = (city or "", state or "", country or "")
                    if key in seen_locations or not any([city, state, country]):
                        continue
                    seen_locations.add(key)
                    locations.append({
                        "city": city,
                        "state": state,
                        "country": country
                    })

            # Fallback to day-wise destination mapping if destination has no mapped locations
            if not locations:
                day_destinations = DestinationPackageMapping.objects.filter(package_id=package.id)
                for destination_mapping in day_destinations:
                    key = (
                        destination_mapping.city or "",
                        destination_mapping.state or "",
                        ""  # country unknown in this mapping
                    )
                    if key in seen_locations or not any(key):
                        continue
                    seen_locations.add(key)
                    locations.append({
                        "city": destination_mapping.city,
                        "state": destination_mapping.state,
                        "country": ""
                    })

            packages_data.append({
                "id": package.id,
                "created_at": package.created_at.isoformat() if package.created_at else None,
                "updated_at": package.updated_at.isoformat() if package.updated_at else None,
                "name": package.name,
                "description": package.description,
                "images": images,
                "destination": {
                    "locations": locations
                }
            })

        response = {"data": packages_data}
        if pagination:
            response["pagination"] = pagination

        return JsonResponse(response, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
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
        packages = packages.order_by('-updated_at')

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
                    package=package, tour_operator_id=tour_operator_id, hotel__location__city=destination.city,day = destination.day
                ).select_related('hotel')

                hotel_data = {
                    "day": destination.day,
                    "city": destination.city,
                    "hotels": [get_hotel_by_id(hotel_mapping.hotel.id) for hotel_mapping in hotels_in_package]
                }
                hotel_details.append(hotel_data)

                # Get only car dealers mapped to this package and tour operator
                cardealers_in_package = PackageCarDealerMapping.objects.filter(
                    package=package, tour_operator_id=tour_operator_id, car_dealer__location__city=destination.city,day = destination.day
                ).select_related('car_dealer')

                cardealer_data = {
                    "day": destination.day,
                    "city": destination.city,
                    "cardealer": [
                        {
                            "id": dealer_mapping.car_dealer.id,
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

                    # Fetch itinerary item images (same pattern as hotels)
                    itinerary_item_images = get_images('itinerary_item', pii.itinerary_item.id, include_binary=False)

                    itinerary_details[pii.day].append({
                        "name": itinerary.name,
                        "type": pii.itinerary_item.item_type,
                        "description": itinerary.description,
                        "charges": float(itinerary.charges or 0),
                        "contact_no": itinerary.contact_no,
                        "sequence": pii.sequence,
                        "location": location,
                        "images": itinerary_item_images,
                        "itinerary_item_id": pii.itinerary_item.id
                    })
                else:
                    itinerary_details[pii.day] = []
            # Sort itinerary details by sequence within each day
            for destination in destinations:
                day= destination.day
                try:
                    activities = itinerary_details[day]
                except:
                    activities = []
                
                activities.sort(key=lambda x: x['sequence'])

                # Find matching hotel and cardealer details for each day
                hotels = next((item['hotels'] for item in hotel_details if item['day'] == day), [])
                cardealers = next((item['cardealer'] for item in cardealer_details if item['day'] == day), [])
                #destionation =  next((dest for dest in destinations if dest.day == day), [])
                # Append day-wise itinerary details
                day_wise_details.append({
                    "day": day,
                    "city":destination.city,
                    "state":destination.state,
                    "title":destination.title,
                    "description":destination.description,
                    "note":destination.note,
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

            # Get package images
            package_images = get_images('package', package.id, include_binary=False)

            # Get package options with hotel mappings
            package_options_data = []
            package_options = PackageOption.objects.filter(package=package).order_by('id')
            for option in package_options:
                # Get hotel mappings for this option, grouped by day
                hotel_mappings_data = []
                hotel_mappings = PackageOptionHotelMapping.objects.filter(
                    package_option=option
                ).select_related('hotel', 'quick_hotel', 'selected_room_type').order_by('day')

                # Group hotels and quick hotels by day
                day_hotel_map = defaultdict(lambda: {"hotel_ids": [], "quick_hotels": []})
                for mapping in hotel_mappings:
                    if mapping.hotel:
                        # New format with room selection details
                        hotel_data = {
                            "hotel_id": mapping.hotel.id,
                            "selected_room_type_id": mapping.selected_room_type.id if mapping.selected_room_type else None,
                            "room_quantity": mapping.room_quantity
                        }
                        # Include room details if room type is selected
                        if mapping.selected_room_type:
                            hotel_data["selected_room_type"] = {
                                "id": mapping.selected_room_type.id,
                                "name": mapping.selected_room_type.name,
                                "type": mapping.selected_room_type.type,
                                "capacity": int(mapping.selected_room_type.capacity) if mapping.selected_room_type.capacity else None,
                                "bedtype": mapping.selected_room_type.bedtype,
                                "price_per_night": mapping.selected_room_type.price_per_night,
                                "description": mapping.selected_room_type.description
                            }
                        day_hotel_map[mapping.day]["hotel_ids"].append(hotel_data)
                    elif mapping.quick_hotel:
                        day_hotel_map[mapping.day]["quick_hotels"].append({
                            "id": mapping.quick_hotel.id,
                            "hotel_name": mapping.quick_hotel.hotel_name,
                            "room_type": mapping.quick_hotel.room_type,
                            "price_per_night": float(mapping.quick_hotel.price_per_night),
                            "total_rooms": mapping.quick_hotel.total_rooms,
                            "address": mapping.quick_hotel.address,
                            "phone": mapping.quick_hotel.phone
                        })

                # Convert to the required format
                for day in sorted(day_hotel_map.keys()):
                    hotel_mappings_data.append({
                        "day": day,
                        "hotel_ids": day_hotel_map[day]["hotel_ids"],
                        "quick_hotels": day_hotel_map[day]["quick_hotels"]
                    })

                package_options_data.append({
                    "id": option.id,
                    "name": option.name,
                    "amount": float(option.amount),
                    "description": option.description,
                    "vehicle_type": option.vehicle_type,
                    "hotel_mappings": hotel_mappings_data
                })

            # Structure final package data
            package_data = {
                "id": package.id,
                "created_at": package.created_at.isoformat() if package.created_at else None,
                "updated_at": package.updated_at.isoformat() if package.updated_at else None,
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
                "terms_and_conditions": package.terms_and_conditions,
                #"destination": destination_details,
                "itinerary_details": day_wise_details,
                "inclusions": package_inclusions,
                "exclusions": package_exclusions,
                "images": package_images,
                "package_options": package_options_data
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
    activity = activity_model.objects.filter(name=name,description=description, tour_operator=tour_operator).first()
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
        required_fields = ["tour_operator_id", "created_by", "name", "type", "destination_id",  "itinerary_items"]
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
                    is_active=data.get('is_active', True),
                    terms_and_conditions=data.get('terms_and_conditions', '')
                )

                # Add Destination mappings
                #for dest in data['destination_mapping']:
                #    DestinationPackageMapping.objects.create(
                #        package_id=package,
                #        destination_id=destination,
                #        tour_operator_id=tour_operator,
                #        day=dest['day'],
                #        city=dest['city'],
                #        state=dest['state']
                #    )

                # Add Itinerary Items
                for itinerary in data['itinerary_items']:
                    day = itinerary['day']
                    DestinationPackageMapping.objects.create(
                        package_id=package,
                        destination_id=destination,
                        tour_operator_id=tour_operator,
                        day=itinerary['day'],
                        city=itinerary.get('city', ''),
                        state=itinerary.get('state', ''),
                        title = itinerary.get('title', ''),
                        description = itinerary.get('description', ''),
                        note = itinerary.get('note', '')
                    )
                    # Process activities within each day
                    for activity in itinerary['activities']:
                        # Default to 'event' type if not specified
                        item_type = activity.get('type', 'event').lower()
                        item_name = activity['name']
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', None)
                        charges = float(activity['charges']) if activity.get('charges') is not None else None

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

                        city, state=itinerary.get('city', ''),itinerary.get('state', '') #get_city_state_from_day(data['destination_mapping'],day)

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

                    # DEPRECATED: Map selected hotels for each day
                    # Frontend now sends hotel data in package_options.hotel_mappings
                    # This code is kept for backward compatibility but will be skipped if array is empty
                    for hotel_id in itinerary.get('hotel_details', []):
                        hotel = Hotel.objects.get(id=hotel_id)
                        PackageHotelMapping.objects.create(
                            package=package,
                            hotel=hotel,
                            day=day,
                            tour_operator=tour_operator,
                            selected_by=created_by
                        )

                    # DEPRECATED: Map selected car dealers for each day
                    # Frontend now sends transport data in package_options.hotel_mappings.transport_ids
                    # This code is kept for backward compatibility but will be skipped if array is empty
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

                # Add Package Options (if provided)
                if "package_options" in data and data['package_options']:
                    for option_data in data['package_options']:
                        # Create the package option
                        package_option = PackageOption.objects.create(
                            package=package,
                            name=option_data['name'],
                            amount=option_data['amount'],
                            description=option_data.get('description', ''),
                            vehicle_type=option_data.get('vehicle_type', ''),
                            tour_operator=tour_operator,
                            created_by=created_by
                        )

                        # Add hotel mappings for this option
                        for hotel_mapping in option_data.get('hotel_mappings', []):
                            day = hotel_mapping['day']

                            # Handle regular hotel IDs with room selections
                            # Support both old format (array of IDs) and new format (array of objects)
                            hotel_ids_data = hotel_mapping.get('hotel_ids', [])
                            for hotel_data in hotel_ids_data:
                                if isinstance(hotel_data, dict):
                                    # New format: {"hotel_id": 1, "selected_room_type_id": 5, "room_quantity": 2}
                                    hotel_id = hotel_data.get('hotel_id')
                                    selected_room_type_id = hotel_data.get('selected_room_type_id')
                                    room_quantity = hotel_data.get('room_quantity')
                                else:
                                    # Old format: just hotel ID (backward compatibility)
                                    hotel_id = hotel_data
                                    selected_room_type_id = None
                                    room_quantity = None

                                hotel = Hotel.objects.get(id=hotel_id)
                                selected_room = Room.objects.get(id=selected_room_type_id) if selected_room_type_id else None

                                PackageOptionHotelMapping.objects.create(
                                    package_option=package_option,
                                    hotel=hotel,
                                    selected_room_type=selected_room,
                                    room_quantity=room_quantity,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
                                )

                            # Handle quick hotel data (already has room_type and total_rooms)
                            for quick_hotel_data in hotel_mapping.get('quick_hotels', []):
                                # Create QuickHotel entry
                                quick_hotel = QuickHotel.objects.create(
                                    tour_operator=tour_operator,
                                    created_by=created_by,
                                    hotel_name=quick_hotel_data['hotel_name'],
                                    room_type=quick_hotel_data['room_type'],
                                    price_per_night=quick_hotel_data['price_per_night'],
                                    total_rooms=quick_hotel_data['total_rooms'],
                                    address=quick_hotel_data.get('address'),
                                    phone=quick_hotel_data.get('phone')
                                )
                                # Create mapping
                                PackageOptionHotelMapping.objects.create(
                                    package_option=package_option,
                                    quick_hotel=quick_hotel,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
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
        required_fields = ["id", "tour_operator_id", "created_by", "name", "type", "destination_id",  "itinerary_items"]
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
                package.terms_and_conditions = data.get('terms_and_conditions', '')
                package.save()

                # Update Destination Mappings
                DestinationPackageMapping.objects.filter(package_id=package).delete()
                #for dest in data['destination_mapping']:
                    #DestinationPackageMapping.objects.create(
                    #    package_id=package,
                    #    destination_id=destination,
                    #    tour_operator_id=tour_operator,
                    #    day=dest['day'],
                    #    city=dest['city'],
                    #    state=dest['state']
                    #)

                # Process Itinerary Items day by day
                for itinerary in data['itinerary_items']:
                    day = itinerary['day']
                    DestinationPackageMapping.objects.create(
                        package_id=package,
                        destination_id=destination,
                        tour_operator_id=tour_operator,
                        day=day,
                        city=itinerary.get('city', ''),
                        state=itinerary.get('state', ''),
                        title = itinerary.get('title', ''),
                        description = itinerary.get('description', ''),
                        note = itinerary.get('note', '')
                    )
                    updated_items = []

                    # Process activities within each day
                    for activity in itinerary['activities']:
                        # Default to 'event' type if not specified
                        item_type = activity.get('type', 'event').lower()
                        item_name = activity['name']
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', None)
                        charges = float(activity['charges']) if activity.get('charges') is not None else None

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

                    # DEPRECATED: Map selected hotels for each day
                    # Frontend now sends hotel data in package_options.hotel_mappings
                    # This code is kept for backward compatibility but will be skipped if array is empty
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

                    # DEPRECATED: Map selected car dealers for each day
                    # Frontend now sends transport data in package_options.hotel_mappings.transport_ids
                    # This code is kept for backward compatibility but will be skipped if array is empty
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

                # Update Package Options (if provided)
                if "package_options" in data:
                    # Delete existing package options and their hotel mappings
                    PackageOption.objects.filter(package=package).delete()

                    # Create new package options
                    for option_data in data['package_options']:
                        # Create the package option
                        package_option = PackageOption.objects.create(
                            package=package,
                            name=option_data['name'],
                            amount=option_data['amount'],
                            description=option_data.get('description', ''),
                            vehicle_type=option_data.get('vehicle_type', ''),
                            tour_operator=tour_operator,
                            created_by=created_by
                        )

                        # Add hotel mappings for this option
                        for hotel_mapping in option_data.get('hotel_mappings', []):
                            day = hotel_mapping['day']

                            # Handle regular hotel IDs with room selections
                            # Support both old format (array of IDs) and new format (array of objects)
                            hotel_ids_data = hotel_mapping.get('hotel_ids', [])
                            for hotel_data in hotel_ids_data:
                                if isinstance(hotel_data, dict):
                                    # New format: {"hotel_id": 1, "selected_room_type_id": 5, "room_quantity": 2}
                                    hotel_id = hotel_data.get('hotel_id')
                                    selected_room_type_id = hotel_data.get('selected_room_type_id')
                                    room_quantity = hotel_data.get('room_quantity')
                                else:
                                    # Old format: just hotel ID (backward compatibility)
                                    hotel_id = hotel_data
                                    selected_room_type_id = None
                                    room_quantity = None

                                hotel = Hotel.objects.get(id=hotel_id)
                                selected_room = Room.objects.get(id=selected_room_type_id) if selected_room_type_id else None

                                PackageOptionHotelMapping.objects.create(
                                    package_option=package_option,
                                    hotel=hotel,
                                    selected_room_type=selected_room,
                                    room_quantity=room_quantity,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
                                )

                            # Handle quick hotel data (already has room_type and total_rooms)
                            for quick_hotel_data in hotel_mapping.get('quick_hotels', []):
                                # Create QuickHotel entry
                                quick_hotel = QuickHotel.objects.create(
                                    tour_operator=tour_operator,
                                    created_by=created_by,
                                    hotel_name=quick_hotel_data['hotel_name'],
                                    room_type=quick_hotel_data['room_type'],
                                    price_per_night=quick_hotel_data['price_per_night'],
                                    total_rooms=quick_hotel_data['total_rooms'],
                                    address=quick_hotel_data.get('address'),
                                    phone=quick_hotel_data.get('phone')
                                )
                                # Create mapping
                                PackageOptionHotelMapping.objects.create(
                                    package_option=package_option,
                                    quick_hotel=quick_hotel,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
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


def delete_package(request):
    """
    Delete a package and all its related records.

    Required fields:
    - package_id: ID of the package to delete
    - tour_operator_id: ID of the tour operator (for verification)

    This will delete:
    - Package record
    - DestinationPackageMapping records
    - Packageitineraryitem records
    - PackageHotelMapping records
    - PackageCarDealerMapping records

    Note: Leads store package snapshots, so deleting a package won't affect existing leads.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        required_keys = ["package_id", "tour_operator_id"]
        missing_keys = set(required_keys) - data.keys()

        if missing_keys:
            return JsonResponse(
                {"error": ",".join(missing_keys) + " is/are required fields."},
                status=400
            )

        package_id = data['package_id']
        tour_operator_id = data['tour_operator_id']

        # Get the package and verify it belongs to the tour operator
        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return JsonResponse(
                {"error": "Package not found."},
                status=404
            )

        if package.tour_operator.id != tour_operator_id:
            return JsonResponse(
                {"error": "Package does not belong to the specified tour operator."},
                status=403
            )

        # Use transaction to ensure all deletes happen atomically
        with transaction.atomic():
            # Delete all related records
            # Delete destination mappings
            DestinationPackageMapping.objects.filter(package_id=package).delete()

            # Delete itinerary items
            Packageitineraryitem.objects.filter(package=package).delete()

            # Delete hotel mappings
            PackageHotelMapping.objects.filter(package=package).delete()

            # Delete car dealer mappings
            PackageCarDealerMapping.objects.filter(package=package).delete()

            # Delete the package itself
            package_name = package.name
            package.delete()

        return JsonResponse(
            {
                "success": f"Package '{package_name}' deleted successfully.",
                "deleted_id": package_id
            },
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
