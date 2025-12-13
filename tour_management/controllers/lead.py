from __future__ import unicode_literals
import json
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
from ..models import (
    Lead, LeadPackage, LeadDestinationMapping, LeadItineraryItem, LeadHotelMapping,
    LeadCarDealerMapping, LeadPackageOption, LeadPackageOptionHotelMapping, LeadPackageOptionCarDealerMapping,
    Customer, Touroperator, User, Destination,
    Hotel, Room, Cardealer, QuickHotel, Inclusion, Exclusion, Event, SightSeeing, Location, Itineraryitem,
    Transaction
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
    """
    Get lead with complete package snapshot.
    Returns the lead data in the same format as package API response.
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body.decode("utf-8"))
            lead_package_id = data.get('lead_package_id')
            lead_id = data.get('lead_id')

            # Get lead package
            if lead_package_id:
                lead_package = LeadPackage.objects.get(uuid=lead_package_id)
            elif lead_id:
                lead = Lead.objects.get(uuid=lead_id)
                lead_package = LeadPackage.objects.filter(lead=lead).first()
                if not lead_package:
                    return JsonResponse({"error": "No package found for this lead"}, status=404)
            else:
                return JsonResponse({"error": "Either lead_package_id or lead_id is required"}, status=400)

            lead = lead_package.lead
            tour_operator_id = str(lead.tour_operator.uuid)
            day_wise_details = []

            # Get destination mappings
            destination_mappings = LeadDestinationMapping.objects.filter(lead_package=lead_package).order_by('day')

            for destination_mapping in destination_mappings:
                day = destination_mapping.day
                city = destination_mapping.city
                state = destination_mapping.state

                # Get hotels for this day with complete details
                hotels_in_lead = LeadHotelMapping.objects.filter(
                    lead_package=lead_package,
                    day=day
                ).select_related('hotel')

                hotel_details = [get_hotel_by_id(hotel_mapping.hotel.id) for hotel_mapping in hotels_in_lead]

                # Get car dealers for this day with complete details
                cardealers_in_lead = LeadCarDealerMapping.objects.filter(
                    lead_package=lead_package,
                    day=day
                ).select_related('car_dealer')

                cardealer_details = [
                    {
                        "id": str(dealer_mapping.car_dealer.uuid),
                        "dealer_name": dealer_mapping.car_dealer.name,
                        "contact_no": dealer_mapping.car_dealer.contact_no,
                        "transport_types": get_transportdetails_from_db(dealer_mapping.car_dealer.id)
                    }
                    for dealer_mapping in cardealers_in_lead
                ]

                # Get activities for this day
                lead_itinerary_items = LeadItineraryItem.objects.filter(
                    lead_package=lead_package,
                    day=day
                ).order_by('sequence')

                activities = []
                for lii in lead_itinerary_items:
                    itinerary = None
                    if lii.itinerary_item.item_type.lower() == 'event':
                        itinerary = Event.objects.filter(id=lii.itinerary_item.item_id).first()
                    elif lii.itinerary_item.item_type.lower() == 'sightseeing':
                        itinerary = SightSeeing.objects.filter(id=lii.itinerary_item.item_id).first()

                    if itinerary:
                        # Build location object
                        location = {}
                        if itinerary.location is not None:
                            location = {
                                "id": str(itinerary.location.uuid),
                                "tour_operator_id": str(itinerary.location.tour_operator.uuid) if itinerary.location.tour_operator else None,
                                "created_by_id": str(itinerary.location.created_by.uuid) if itinerary.location.created_by else None,
                                "city": itinerary.location.city,
                                "state": itinerary.location.state,
                                "country": itinerary.location.country,
                                "pin_code": itinerary.location.pin_code,
                                "name": itinerary.location.name,
                                "address": itinerary.location.address,
                                "lng": itinerary.location.lng,
                                "lat": itinerary.location.lat,
                            }

                        # Get activity images
                        activity_images = get_images(lii.itinerary_item.item_type, itinerary.id, include_binary=False)

                        activities.append({
                            "name": itinerary.name,
                            "type": lii.itinerary_item.item_type,
                            "description": itinerary.description,
                            "charges": float(itinerary.charges or 0),
                            "contact_no": itinerary.contact_no,
                            "sequence": lii.sequence,
                            "location": location,
                            "images": activity_images,
                            "itinerary_item_id": str(lii.itinerary_item.uuid)
                        })

                # Build day-wise details
                day_wise_details.append({
                    "day": day,
                    "city": city,
                    "state": state,
                    "title": destination_mapping.title,
                    "description": destination_mapping.description,
                    "note": destination_mapping.note,
                    "activities": activities,
                    "hotel_details": hotel_details,
                    "car_dealers": cardealer_details
                })

            # Get package options with hotel mappings
            package_options_data = []
            lead_package_options = LeadPackageOption.objects.filter(lead_package=lead_package).order_by('id')
            for option in lead_package_options:
                # Get hotel mappings for this option, grouped by day
                hotel_mappings_data = []
                hotel_mappings = LeadPackageOptionHotelMapping.objects.filter(
                    lead_package_option=option
                ).select_related('hotel', 'selected_room_type').order_by('day')

                # Group hotels and quick hotels by day
                day_hotel_map = defaultdict(lambda: {"hotel_ids": [], "quick_hotels": []})
                for mapping in hotel_mappings:
                    if mapping.hotel:
                        # Include room selection details
                        hotel_data = {
                            "hotel_id": str(mapping.hotel.uuid),
                            "selected_room_type_id": str(mapping.selected_room_type.uuid) if mapping.selected_room_type else None,
                            "room_quantity": mapping.room_quantity
                        }
                        # Include room snapshot if available
                        if mapping.room_snapshot:
                            hotel_data["selected_room_type"] = mapping.room_snapshot
                        day_hotel_map[mapping.day]["hotel_ids"].append(hotel_data)
                    elif mapping.quick_hotel_data:
                        day_hotel_map[mapping.day]["quick_hotels"].append(mapping.quick_hotel_data)

                # Convert to the required format
                for day in sorted(day_hotel_map.keys()):
                    hotel_mappings_data.append({
                        "day": day,
                        "hotel_ids": day_hotel_map[day]["hotel_ids"],
                        "quick_hotels": day_hotel_map[day]["quick_hotels"]
                    })

                package_options_data.append({
                    "id": str(option.uuid),
                    "name": option.name,
                    "amount": float(option.amount),
                    "description": option.description,
                    "vehicle_type": option.vehicle_type,
                    "hotel_mappings": hotel_mappings_data
                })

            # Enrich hotel mappings with full details for PDF generation
            for option_data in package_options_data:
                for day_mapping in option_data['hotel_mappings']:
                    # Process regular hotels
                    enriched_hotels = []
                    for hotel_info in day_mapping['hotel_ids']:
                        hotel_id = hotel_info['hotel_id']
                        # Fetch full hotel details
                        # Assuming get_hotel_by_id can check UUID if we modify it, OR we need to resolve UUID here.
                        # Since hotel_id above is now UUID (from line 195/196), we need to change how we fetch.
                        # Wait, get_hotel_by_id is likely using ID. I need to check `hotel.py`.
                        # If I change hotel_id in response to UUID, then here 'hotel_id' is UUID.
                        # But get_hotel_by_id probably expects Integer ID?
                        # I will address this by fetching the Hotel object by UUID first, then passing its ID to get_hotel_by_id (if get_hotel_by_id needs ID)
                        # OR update get_hotel_by_id to support UUID.
                        # For now, let's look up the hotel by UUID to get the object.
                        hotel_obj = Hotel.objects.get(uuid=hotel_id)
                        full_hotel_details = get_hotel_by_id(hotel_obj.id)
                        
                        # Merge room selection if available
                        if 'selected_room_type' in hotel_info:
                            full_hotel_details['selected_room_snapshot'] = hotel_info['selected_room_type']
                        elif 'selected_room_type_id' in hotel_info:
                            # Try to find the selected room in the fetched rooms
                            rooms = full_hotel_details.get('rooms', [])
                            selected_room = next((r for r in rooms if r['id'] == hotel_info['selected_room_type_id']), None)
                            if selected_room:
                                full_hotel_details['selected_room_data'] = selected_room
                        
                        full_hotel_details['room_quantity'] = hotel_info.get('room_quantity')
                        enriched_hotels.append(full_hotel_details)
                    
                    # Replace the basic ID list with enriched details
                    day_mapping['hotels_detailed'] = enriched_hotels

            # Structure final lead package data (matching package API response format)
            lead_package_data = {
                "id": str(lead_package.uuid),
                "name": lead_package.name,
                "destination_id": str(lead_package.destination.uuid) if lead_package.destination else None,
                "description": lead_package.description,
                "pax_size": lead_package.pax_size,
                "contains_travel_fare": lead_package.contains_travel_fare,
                "transport_type": lead_package.transport_type,
                "no_of_days": lead_package.no_of_days,
                "package_amount": float(lead_package.package_amount or 0),
                "type": lead_package.type,
                "terms_and_conditions": lead_package.terms_and_conditions,
                "itinerary_details": day_wise_details,
                "inclusions": lead_package.package_inclusions or [],
                "exclusions": lead_package.package_exclusions or [],
                "images": lead_package.package_images or [],
                "amenities": lead_package.package_amenities or [],
                "policies": lead_package.package_policies or [],
                "package_options": package_options_data
            }

            # Include lead metadata
            response_data = {
                "lead_id": str(lead.uuid),
                "customer": {
                    "id": str(lead.customer.uuid),
                    "name": lead.customer.name,
                    "phone": lead.customer.phone,
                    "email": lead.customer.email,
                    "address": lead.customer.address
                },
                "status": lead.status,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
                "travel_start_date": lead.travel_start_date.isoformat() if lead.travel_start_date else None,
                "travel_end_date": lead.travel_end_date.isoformat() if lead.travel_end_date else None,
                "package": lead_package_data
            }

            return JsonResponse(response_data, status=200)

    except LeadPackage.DoesNotExist:
        return JsonResponse({"error": "Lead package not found"}, status=404)
    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def get_all_leads(request):
    """
    Get all leads for a tour operator with limited details for card display.
    Returns paginated list of leads with basic package and customer information.
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body.decode("utf-8"))
            tour_operator_id = data.get('tour_operator_id')

            if not tour_operator_id:
                return JsonResponse({"error": "tour_operator_id is required"}, status=400)

            # Verify tour operator exists
            tour_operator = Touroperator.objects.get(uuid=tour_operator_id)

            # Get all leads for this tour operator
            leads = Lead.objects.filter(tour_operator=tour_operator).select_related(
                'customer', 'created_by'
            ).order_by('-created_at')

            # Optional filters
            status = data.get('status')
            if status:
                leads = leads.filter(status=status)

            customer_id = data.get('customer_id')
            if customer_id:
                leads = leads.filter(customer_id=customer_id)

            # Manual pagination
            page = data.get('page', 1)
            page_size = data.get('page_size', 10)

            # Calculate pagination
            total_count = leads.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            paginated_leads = leads[start_index:end_index]

            # Build response with limited details for cards
            leads_data = []
            for lead in paginated_leads:
                # Get lead package
                lead_package = LeadPackage.objects.filter(lead=lead).first()

                if lead_package:
                    # Get first image from package images
                    package_images = lead_package.package_images or []
                    first_image = package_images[0] if package_images else None

                    # Count hotels and activities
                    total_hotels = LeadHotelMapping.objects.filter(lead_package=lead_package).count()
                    total_activities = LeadItineraryItem.objects.filter(lead_package=lead_package).count()

                    package_data = {
                        "id": str(lead_package.uuid),
                        "name": lead_package.name,
                        "description": lead_package.description,
                        "type": lead_package.type,
                        "no_of_days": lead_package.no_of_days,
                        "package_amount": float(lead_package.package_amount or 0),
                        "destination": {
                            "id": str(lead_package.destination.uuid) if lead_package.destination else None,
                            "name": lead_package.destination.name if lead_package.destination else None
                        },
                        "image": first_image,
                        "total_hotels": total_hotels,
                        "total_activities": total_activities
                    }
                else:
                    package_data = None

                # Build lead card data
                lead_data = {
                    "lead_id": str(lead.uuid),
                    "status": lead.status,
                    "created_at": lead.created_at.isoformat() if lead.created_at else None,
                    "travel_start_date": lead.travel_start_date.isoformat() if lead.travel_start_date else None,
                    "travel_end_date": lead.travel_end_date.isoformat() if lead.travel_end_date else None,
                    "customer": {
                        "id": str(lead.customer.uuid),
                        "name": lead.customer.name,
                        "phone": lead.customer.phone,
                        "email": lead.customer.email
                    },
                    "created_by": {
                        "id": str(lead.created_by.uuid) if lead.created_by else None,
                        "username": lead.created_by.username if lead.created_by else None
                    },
                    "package": package_data
                }
                leads_data.append(lead_data)

            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1

            return JsonResponse({
                "count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_previous": has_previous,
                "leads": leads_data
            })

        return JsonResponse({"error": "Invalid request method"}, status=405)

    except Touroperator.DoesNotExist:
        return JsonResponse({"error": "Tour operator not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_lead(request):
    """
    Update a lead with modified package snapshot.
    Allows updating package details, hotel selections, transportation selections, and activities.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Validate required fields
        required_fields = ["lead_id", "created_by", "package_snapshot"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Fetch lead and lead package
                lead_id = data['lead_id']

                # Check if lead exists
                if not Lead.objects.filter(uuid=lead_id).exists():
                    return JsonResponse({
                        "error": f"Lead with id {lead_id} not found"
                    }, status=404)

                lead = Lead.objects.get(uuid=lead_id)

                # Get the lead package for this lead
                lead_package = LeadPackage.objects.filter(lead=lead).first()
                if not lead_package:
                    return JsonResponse({
                        "error": f"No package found for lead {lead_id}"
                    }, status=404)

                created_by = User.objects.get(uuid=data['created_by'])
                tour_operator = lead_package.tour_operator

                # Get package snapshot
                pkg_snapshot = data['package_snapshot']

                # Update lead status and travel dates if provided
                if 'status' in data:
                    lead_package.lead.status = data['status']
                if 'travel_start_date' in data:
                    lead_package.lead.travel_start_date = data['travel_start_date']
                if 'travel_end_date' in data:
                    lead_package.lead.travel_end_date = data['travel_end_date']
                lead_package.lead.save()

                # Update LeadPackage basic fields
                lead_package.name = pkg_snapshot.get('name', lead_package.name)
                lead_package.description = pkg_snapshot.get('description', lead_package.description)
                lead_package.type = pkg_snapshot.get('type', lead_package.type)
                lead_package.pax_size = pkg_snapshot.get('pax_size', lead_package.pax_size)
                lead_package.contains_travel_fare = pkg_snapshot.get('contains_travel_fare', lead_package.contains_travel_fare)
                lead_package.transport_type = pkg_snapshot.get('transport_type', lead_package.transport_type)
                lead_package.no_of_days = pkg_snapshot.get('no_of_days', lead_package.no_of_days)
                lead_package.package_amount = pkg_snapshot.get('package_amount', lead_package.package_amount)
                lead_package.notes = pkg_snapshot.get('notes', lead_package.notes)
                lead_package.terms_and_conditions = pkg_snapshot.get('terms_and_conditions', lead_package.terms_and_conditions)

                # Update snapshot fields
                lead_package.package_images = pkg_snapshot.get('images', lead_package.package_images)
                lead_package.package_inclusions = pkg_snapshot.get('inclusions', lead_package.package_inclusions)
                lead_package.package_exclusions = pkg_snapshot.get('exclusions', lead_package.package_exclusions)
                lead_package.package_amenities = pkg_snapshot.get('amenities', lead_package.package_amenities)
                lead_package.package_policies = pkg_snapshot.get('policies', lead_package.package_policies)
                lead_package.save()

                # Clear existing mappings
                LeadDestinationMapping.objects.filter(lead_package=lead_package).delete()
                LeadItineraryItem.objects.filter(lead_package=lead_package).delete()
                LeadHotelMapping.objects.filter(lead_package=lead_package).delete()
                LeadCarDealerMapping.objects.filter(lead_package=lead_package).delete()

                # Process itinerary from package snapshot
                # Support both 'itinerary_details' (from GET response) and 'itinerary_items' (from ADD/UPDATE request)
                itinerary_data = pkg_snapshot.get('itinerary_items') or pkg_snapshot.get('itinerary_details', [])

                if not itinerary_data:
                    return JsonResponse({
                        "error": "No itinerary data found. Please provide either 'itinerary_items' or 'itinerary_details' in package_snapshot"
                    }, status=400)

                for day_data in itinerary_data:
                    day = day_data.get('day')
                    city = day_data.get('city', '')
                    state = day_data.get('state', '')
                    title = day_data.get('title', '')
                    description = day_data.get('description', '')
                    note = day_data.get('note', '')

                    # Create destination mapping for this day
                    LeadDestinationMapping.objects.create(
                        lead_package=lead_package,
                        destination=lead_package.destination,
                        tour_operator=tour_operator,
                        day=day,
                        city=city,
                        state=state,
                        title=title,
                        description=description,
                        note=note
                    )

                    # Process activities for this day
                    activities = day_data.get('activities', [])
                    for activity in activities:
                        # Default to 'event' type if not specified
                        item_type = activity.get('type', 'event').lower()
                        item_name = activity.get('name', '')
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', None)
                        charges = float(activity['charges']) if activity.get('charges') is not None else None
                        sequence = activity.get('sequence', 0)

                        # Location management
                        location = None
                        if "location" in activity and activity['location']:
                            location = get_or_create_location(tour_operator, created_by, activity['location'])

                        # Determine if it's an event or sightseeing activity
                        item_id = None
                        if item_type == "event":
                            event = get_or_create_activity(Event, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = event.id
                        elif item_type == "sightseeing":
                            sightseeing = get_or_create_activity(SightSeeing, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = sightseeing.id

                        if item_id:
                            # Get or create itinerary item
                            itinerary_item = Itineraryitem.objects.filter(
                                item_id=item_id,
                                item_type=item_type,
                                city=city,
                                state=state,
                                tour_operator_id=tour_operator,
                                destination=lead_package.destination
                            ).first()

                            if not itinerary_item:
                                itinerary_item = Itineraryitem.objects.create(
                                    tour_operator_id=tour_operator,
                                    created_by=created_by,
                                    destination=lead_package.destination,
                                    city=city,
                                    state=state,
                                    item_type=item_type,
                                    item_id=item_id,
                                    description=item_description
                                )

                            # Create lead itinerary item
                            LeadItineraryItem.objects.create(
                                lead_package=lead_package,
                                itinerary_item=itinerary_item,
                                created_by=created_by,
                                day=day,
                                sequence=sequence
                            )

                    # Map hotels for this day (support multiple hotels)
                    hotel_details = day_data.get('hotel_details', [])
                    for hotel_data in hotel_details:
                        # hotel_data can be either an ID or a full hotel object
                        hotel_id = hotel_data if isinstance(hotel_data, int) else hotel_data.get('id')
                        if hotel_id:
                            hotel = Hotel.objects.get(id=hotel_id)
                            LeadHotelMapping.objects.create(
                                lead_package=lead_package,
                                hotel=hotel,
                                day=day,
                                tour_operator=tour_operator,
                                selected_by=created_by
                            )

                    # Map car dealers for this day (support multiple car dealers)
                    car_dealers = day_data.get('car_dealers', [])
                    for car_dealer_data in car_dealers:
                        # car_dealer_data can be either an ID or a full car dealer object
                        car_dealer_id = car_dealer_data if isinstance(car_dealer_data, int) else car_dealer_data.get('id')
                        if car_dealer_id:
                            car_dealer = Cardealer.objects.get(id=car_dealer_id)
                            LeadCarDealerMapping.objects.create(
                                lead_package=lead_package,
                                car_dealer=car_dealer,
                                tour_operator=tour_operator,
                                day=day,
                                selected_by=created_by
                            )

                # Update Package Options (if provided in snapshot)
                if "package_options" in pkg_snapshot:
                    # Delete existing package option hotel mappings first (to avoid protected foreign key error)
                    existing_options = LeadPackageOption.objects.filter(lead_package=lead_package)
                    for option in existing_options:
                        LeadPackageOptionHotelMapping.objects.filter(lead_package_option=option).delete()

                    # Now delete the package options
                    existing_options.delete()

                    # Create new package options
                    for option_data in pkg_snapshot['package_options']:
                        # Create the lead package option
                        lead_package_option = LeadPackageOption.objects.create(
                            lead_package=lead_package,
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
                            hotel_ids_data = hotel_mapping.get('hotel_ids', [])
                            for hotel_data in hotel_ids_data:
                                if isinstance(hotel_data, dict):
                                    # New format: {"hotel_id": 1, "selected_room_type_id": 5, "room_quantity": 2, "selected_room_type": {...}}
                                    hotel_id = hotel_data.get('hotel_id')
                                    selected_room_type_id = hotel_data.get('selected_room_type_id')
                                    room_quantity = hotel_data.get('room_quantity')
                                    room_snapshot = hotel_data.get('selected_room_type')
                                else:
                                    # Old format: just hotel ID
                                    hotel_id = hotel_data
                                    selected_room_type_id = None
                                    room_quantity = None
                                    room_snapshot = None

                                hotel = Hotel.objects.get(id=hotel_id)
                                selected_room = Room.objects.get(id=selected_room_type_id) if selected_room_type_id else None

                                LeadPackageOptionHotelMapping.objects.create(
                                    lead_package_option=lead_package_option,
                                    hotel=hotel,
                                    selected_room_type=selected_room,
                                    room_quantity=room_quantity,
                                    room_snapshot=room_snapshot,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
                                )

                            # Handle quick hotel data
                            for quick_hotel_data in hotel_mapping.get('quick_hotels', []):
                                LeadPackageOptionHotelMapping.objects.create(
                                    lead_package_option=lead_package_option,
                                    quick_hotel_data=quick_hotel_data,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
                                )

                # Response after successful update
                return JsonResponse({
                    "message": "Lead updated successfully",
                    "lead_id": str(lead_package.lead.uuid),
                    "lead_package_id": str(lead_package.uuid)
                }, status=200)

        except LeadPackage.DoesNotExist:
            return JsonResponse({"error": "Lead package not found"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Destination.DoesNotExist:
            return JsonResponse({"error": "Destination not found"}, status=404)
        except Hotel.DoesNotExist:
            return JsonResponse({"error": "One or more hotels not found"}, status=404)
        except Cardealer.DoesNotExist:
            return JsonResponse({"error": "One or more car dealers not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def add_lead(request):
    """
    Create a lead with a complete package snapshot.
    Accepts package data (matching package API response structure) and allows multiple hotels/transportations per day.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Validate required fields
        required_fields = ["tour_operator_id", "created_by", "customer_id", "package_snapshot"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Fetch main entities
                tour_operator = Touroperator.objects.get(uuid=data['tour_operator_id'])
                created_by = User.objects.get(uuid=data['created_by'])
                customer = Customer.objects.get(uuid=data['customer_id'])

                # Get package snapshot
                pkg_snapshot = data['package_snapshot']

                # Get destination
                destination_id = pkg_snapshot.get('destination_id')
                if not destination_id:
                    return JsonResponse({"error": "destination_id is required in package_snapshot"}, status=400)
                destination = Destination.objects.get(uuid=destination_id)

                # Create the Lead record
                lead = Lead.objects.create(
                    customer=customer,
                    tour_operator=tour_operator,
                    created_by=created_by,
                    status=data.get("status", "new"),  # Default to 'new' status
                    travel_start_date=data.get("travel_start_date"),
                    travel_end_date=data.get("travel_end_date")
                )

                # Create LeadPackage with snapshot data
                lead_package = LeadPackage.objects.create(
                    lead=lead,
                    tour_operator=tour_operator,
                    created_by=created_by,
                    destination=destination,
                    name=pkg_snapshot.get('name', ''),
                    description=pkg_snapshot.get('description', ''),
                    type=pkg_snapshot.get('type', ''),
                    pax_size=pkg_snapshot.get('pax_size'),
                    contains_travel_fare=pkg_snapshot.get('contains_travel_fare', False),
                    transport_type=pkg_snapshot.get('transport_type', ''),
                    no_of_days=pkg_snapshot.get('no_of_days', 0),
                    package_amount=pkg_snapshot.get('package_amount', 0.0),
                    notes=pkg_snapshot.get('notes', ''),
                    terms_and_conditions=pkg_snapshot.get('terms_and_conditions', ''),
                    # Store snapshot data as JSON
                    package_images=pkg_snapshot.get('images', []),
                    package_inclusions=pkg_snapshot.get('inclusions', []),
                    package_exclusions=pkg_snapshot.get('exclusions', []),
                    package_amenities=pkg_snapshot.get('amenities', []),
                    package_policies=pkg_snapshot.get('policies', [])
                )

                # Process itinerary from package snapshot
                # Support both 'itinerary_items' (from ADD/UPDATE request) and 'itinerary_details' (from GET response)
                itinerary_data = pkg_snapshot.get('itinerary_items') or pkg_snapshot.get('itinerary_details', [])
                for day_data in itinerary_data:
                    day = day_data.get('day')
                    city = day_data.get('city', '')
                    state = day_data.get('state', '')
                    title = day_data.get('title', '')
                    description = day_data.get('description', '')
                    note = day_data.get('note', '')

                    # Create destination mapping for this day
                    LeadDestinationMapping.objects.create(
                        lead_package=lead_package,
                        destination=destination,
                        tour_operator=tour_operator,
                        day=day,
                        city=city,
                        state=state,
                        title=title,
                        description=description,
                        note=note
                    )

                    # Process activities for this day
                    activities = day_data.get('activities', [])
                    for activity in activities:
                        # Default to 'event' type if not specified
                        item_type = activity.get('type', 'event').lower()
                        item_name = activity.get('name', '')
                        item_description = activity.get('description', '')
                        contact_no = activity.get('contact_no', None)
                        charges = float(activity['charges']) if activity.get('charges') is not None else None
                        sequence = activity.get('sequence', 0)

                        # Location management
                        location = None
                        if "location" in activity and activity['location']:
                            location = get_or_create_location(tour_operator, created_by, activity['location'])

                        # Determine if it's an event or sightseeing activity
                        item_id = None
                        if item_type == "event":
                            event = get_or_create_activity(Event, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = event.id
                        elif item_type == "sightseeing":
                            sightseeing = get_or_create_activity(SightSeeing, tour_operator, created_by, item_name, item_description, location, charges, contact_no)
                            item_id = sightseeing.id

                        if item_id:
                            # Get or create itinerary item
                            itinerary_item = Itineraryitem.objects.filter(
                                item_id=item_id,
                                item_type=item_type,
                                city=city,
                                state=state,
                                tour_operator_id=tour_operator,
                                destination=destination
                            ).first()

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

                            # Create lead itinerary item
                            LeadItineraryItem.objects.create(
                                lead_package=lead_package,
                                itinerary_item=itinerary_item,
                                created_by=created_by,
                                day=day,
                                sequence=sequence
                            )

                    # Map hotels for this day (support multiple hotels)
                    hotel_details = day_data.get('hotel_details', [])
                    for hotel_data in hotel_details:
                        # hotel_data can be either an ID or a full hotel object
                        hotel_id = hotel_data if isinstance(hotel_data, int) else hotel_data.get('id')
                        if hotel_id:
                            hotel = Hotel.objects.get(uuid=hotel_id)
                            LeadHotelMapping.objects.create(
                                lead_package=lead_package,
                                hotel=hotel,
                                day=day,
                                tour_operator=tour_operator,
                                selected_by=created_by
                            )

                    # Map car dealers for this day (support multiple car dealers)
                    car_dealers = day_data.get('car_dealers', [])
                    for car_dealer_data in car_dealers:
                        # car_dealer_data can be either an ID or a full car dealer object
                        car_dealer_id = car_dealer_data if isinstance(car_dealer_data, int) else car_dealer_data.get('id')
                        if car_dealer_id:
                            car_dealer = Cardealer.objects.get(uuid=car_dealer_id)
                            LeadCarDealerMapping.objects.create(
                                lead_package=lead_package,
                                car_dealer=car_dealer,
                                tour_operator=tour_operator,
                                day=day,
                                selected_by=created_by
                            )

                # Add Package Options (if provided in snapshot)
                if "package_options" in pkg_snapshot and pkg_snapshot['package_options']:
                    for option_data in pkg_snapshot['package_options']:
                        # Create the lead package option
                        lead_package_option = LeadPackageOption.objects.create(
                            lead_package=lead_package,
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
                                    # New format: {"hotel_id": 1, "selected_room_type_id": 5, "room_quantity": 2, "selected_room_type": {...}}
                                    hotel_id = hotel_data.get('hotel_id')
                                    selected_room_type_id = hotel_data.get('selected_room_type_id')
                                    room_quantity = hotel_data.get('room_quantity')
                                    room_snapshot = hotel_data.get('selected_room_type')  # Full room details from package response
                                else:
                                    # Old format: just hotel ID (backward compatibility)
                                    hotel_id = hotel_data
                                    selected_room_type_id = None
                                    room_quantity = None
                                    room_snapshot = None
                                
                                hotel = Hotel.objects.get(uuid=hotel_id)
                                selected_room = Room.objects.get(uuid=selected_room_type_id) if selected_room_type_id else None

                                LeadPackageOptionHotelMapping.objects.create(
                                    lead_package_option=lead_package_option,
                                    hotel=hotel,
                                    selected_room_type=selected_room,
                                    room_quantity=room_quantity,
                                    room_snapshot=room_snapshot,  # Store complete room details as snapshot
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
                                )

                            # Handle quick hotel data (snapshot as JSON - already has room_type and total_rooms)
                            for quick_hotel_data in hotel_mapping.get('quick_hotels', []):
                                # Store quick hotel data as JSON snapshot
                                LeadPackageOptionHotelMapping.objects.create(
                                    lead_package_option=lead_package_option,
                                    quick_hotel_data=quick_hotel_data,
                                    day=day,
                                    tour_operator=tour_operator,
                                    selected_by=created_by
                                )

                # Response after successful lead creation
                return JsonResponse({
                    "message": "Lead created successfully",
                    "lead_id": str(lead.uuid),
                    "lead_package_id": str(lead_package.uuid)
                }, status=201)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Tour operator not found"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Customer.DoesNotExist:
            return JsonResponse({"error": "Customer not found"}, status=404)
        except Destination.DoesNotExist:
            return JsonResponse({"error": "Destination not found"}, status=404)
        except Hotel.DoesNotExist:
            return JsonResponse({"error": "One or more hotels not found"}, status=404)
        except Cardealer.DoesNotExist:
            return JsonResponse({"error": "One or more car dealers not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def delete_lead(request):
    """
    Delete a lead and all its related records.

    Required fields:
    - lead_id: ID of the lead to delete
    - tour_operator_id: ID of the tour operator (for verification)

    This will delete:
    - Lead record
    - LeadPackage records
    - LeadDestinationMapping records
    - LeadItineraryItem records
    - LeadHotelMapping records
    - LeadCarDealerMapping records

    Cannot delete if:
    - Lead is referenced by any Transaction (booking)
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        required_keys = ["lead_id", "tour_operator_id"]
        missing_keys = set(required_keys) - data.keys()

        if missing_keys:
            return JsonResponse(
                {"error": ",".join(missing_keys) + " is/are required fields."},
                status=400
            )

        lead_id = data['lead_id']
        tour_operator_id = data['tour_operator_id']

        # Get the lead and verify it belongs to the tour operator
        try:
            lead = Lead.objects.get(uuid=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse(
                {"error": "Lead not found."},
                status=404
            )

        if lead.tour_operator.uuid != tour_operator_id:
            return JsonResponse(
                {"error": "Lead does not belong to the specified tour operator."},
                status=403
            )

        # Check if lead is referenced by any transactions (bookings)
        transaction_count = Transaction.objects.filter(lead=lead).count()
        if transaction_count > 0:
            return JsonResponse(
                {
                    "error": f"Cannot delete lead. It is referenced by {transaction_count} booking(s).",
                    "referenced_by": "transactions",
                    "count": transaction_count
                },
                status=409
            )

        # Get all lead packages for this lead
        lead_packages = LeadPackage.objects.filter(lead=lead)

        # Use transaction to ensure all deletes happen atomically
        with transaction.atomic():
            # Delete all related records for each lead package
            for lead_package in lead_packages:
                # Delete destination mappings
                LeadDestinationMapping.objects.filter(lead_package=lead_package).delete()

                # Delete itinerary items
                LeadItineraryItem.objects.filter(lead_package=lead_package).delete()

                # Delete hotel mappings
                LeadHotelMapping.objects.filter(lead_package=lead_package).delete()

                # Delete car dealer mappings
                LeadCarDealerMapping.objects.filter(lead_package=lead_package).delete()

                # Delete the lead package itself
                lead_package.delete()

            # Finally, delete the lead
            customer_name = lead.customer.name if lead.customer else "Unknown"
            lead.delete()

        return JsonResponse(
            {
                "success": f"Lead for customer '{customer_name}' deleted successfully.",
                "deleted_id": lead_id
            },
            status=200
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
