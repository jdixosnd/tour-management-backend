from django.db import transaction
from django.http import JsonResponse
from ..models import (
    Customer, Package, Destination, Touroperator, User, Location,
    Transaction, TransactionItineraryItem, Event, SightSeeing,
    Inclusion, Exclusion, Amenity, Policy, Hotel, Cardealer, Room, CarType,
    Packageitineraryitem, DestinationPackageMapping, Lead, LeadPackage
)
from .hotel import get_images
import json
def add_transaction(request):
    """
    DEPRECATED: This function uses the old Transaction model structure.
    Please use the new transaction API that works with Leads.

    New workflow:
    1. Create a Lead with multiple hotel/transport options
    2. Customer selects their preferences
    3. Create Transaction with customer's selections

    See docs/transaction_api_update_for_ui.md for details.
    """
    return JsonResponse({
        "error": "This API is deprecated. Please use the new Lead-based transaction workflow.",
        "message": "Transaction model has been updated to work with Leads. See documentation for migration guide.",
        "documentation": "docs/transaction_api_update_for_ui.md"
    }, status=410)  # 410 Gone - indicates the resource is no longer available

def add_transaction_old(request):
    """
    OLD IMPLEMENTATION - Kept for reference only
    Create a transaction as a complete snapshot of a package.
    Accepts the complete package structure (matching package API response) and allows customization.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        # Required fields
        required_fields = ["customer_id", "created_by", "tour_operator", "package_snapshot"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Get and validate the main entities
                customer = Customer.objects.get(id=data['customer_id'], tour_operator=data['tour_operator'])
                created_by = User.objects.get(id=data['created_by'])
                tour_operator = Touroperator.objects.get(id=data['tour_operator'])

                # Get package snapshot from request
                pkg_snapshot = data['package_snapshot']

                # Get references to original package and destination (if provided)
                package = None
                destination = None
                if pkg_snapshot.get('id'):
                    package = Package.objects.filter(id=pkg_snapshot['id'], tour_operator=tour_operator).first()
                if pkg_snapshot.get('destination_id'):
                    destination = Destination.objects.filter(id=pkg_snapshot['destination_id'], tour_operator_id=tour_operator).first()

                # Create the Transaction snapshot with all package data
                transaction_instance = Transaction.objects.create(
                    customer=customer,
                    package=package,
                    destination=destination,
                    created_by=created_by,
                    tour_operator=tour_operator,
                    package_name=pkg_snapshot.get("name", ""),
                    package_description=pkg_snapshot.get("description", ""),
                    package_type=pkg_snapshot.get("type", ""),
                    pax_size=pkg_snapshot.get("pax_size"),
                    contains_travel_fare=pkg_snapshot.get("contains_travel_fare", False),
                    transport_type=pkg_snapshot.get("transport_type", ""),
                    no_of_days=pkg_snapshot.get("no_of_days", 0),
                    package_amount=pkg_snapshot.get("package_amount", 0.0),
                    proposed_package_amount=data.get("proposed_package_amount", pkg_snapshot.get("package_amount", 0.0)),
                    original_package_amount=data.get("original_package_amount", pkg_snapshot.get("package_amount", 0.0)),
                    discount_amount=data.get("discount_amount", 0.0),
                    margin_of_profit=data.get("margin_of_profit", 0.0),
                    taxes=data.get("taxes", 0.0),
                    final_amount=data.get("final_amount", pkg_snapshot.get("package_amount", 0.0)),
                    package_inclusions=pkg_snapshot.get("inclusions", []),
                    package_exclusions=pkg_snapshot.get("exclusions", []),
                    package_images=pkg_snapshot.get("images", [])
                )

                # Process each day in itinerary_details from package snapshot
                for day_detail in pkg_snapshot.get("itinerary_details", []):
                    day = day_detail.get("day")

                    # Get day-wise metadata
                    city = day_detail.get("city", "")
                    state = day_detail.get("state", "")
                    title = day_detail.get("title", "")
                    description = day_detail.get("description", "")
                    note = day_detail.get("note", "")

                    # Process hotel details - get first hotel from the list (or allow selection)
                    hotel_details_list = day_detail.get("hotel_details", [])
                    if not hotel_details_list:
                        continue  # Skip if no hotel for this day

                    # Use the first hotel or allow customization via 'selected_hotel_index'
                    selected_hotel_idx = day_detail.get("selected_hotel_index", 0)
                    hotel_data = hotel_details_list[selected_hotel_idx] if selected_hotel_idx < len(hotel_details_list) else hotel_details_list[0]

                    # Get hotel and room references (if IDs are provided)
                    hotel = None
                    room = None
                    if hotel_data.get('id'):
                        hotel = Hotel.objects.filter(id=hotel_data['id']).first()

                    # Get selected room from hotel rooms
                    room_data = hotel_data.get("room", {})
                    if isinstance(hotel_data.get("rooms"), list) and len(hotel_data.get("rooms", [])) > 0:
                        selected_room_idx = day_detail.get("selected_room_index", 0)
                        room_data = hotel_data["rooms"][selected_room_idx] if selected_room_idx < len(hotel_data["rooms"]) else hotel_data["rooms"][0]

                    if room_data.get('id'):
                        room = Room.objects.filter(id=room_data['id']).first()

                    # Process car dealer details
                    car_dealers_list = day_detail.get("car_dealers", [])
                    car_dealer = None
                    car_type = None
                    car_dealer_data = {}
                    car_dealer_transport_types = []

                    if car_dealers_list:
                        selected_dealer_idx = day_detail.get("selected_car_dealer_index", 0)
                        car_dealer_data = car_dealers_list[selected_dealer_idx] if selected_dealer_idx < len(car_dealers_list) else car_dealers_list[0]

                        if car_dealer_data.get('id'):
                            car_dealer = Cardealer.objects.filter(id=car_dealer_data['id']).first()

                        car_dealer_transport_types = car_dealer_data.get("transport_types", [])

                        # Get selected transport type
                        if car_dealer_transport_types:
                            selected_transport_idx = day_detail.get("selected_transport_index", 0)
                            transport_data = car_dealer_transport_types[selected_transport_idx] if selected_transport_idx < len(car_dealer_transport_types) else car_dealer_transport_types[0]
                            if transport_data.get('type'):
                                car_type = CarType.objects.filter(name=transport_data['type']).first()

                    # Extract location data from hotel_data
                    location_data = hotel_data.get("location", {})

                    # Create TransactionDayDetails for each day with complete snapshot
                    day_instance = TransactionDayDetails.objects.create(
                        transaction=transaction_instance,
                        day=day,
                        city=city,
                        state=state,
                        title=title,
                        description=description,
                        note=note,
                        hotel=hotel,
                        hotel_name=hotel_data.get("name", ""),
                        hotel_description=hotel_data.get("description", ""),
                        hotel_ratings=hotel_data.get("ratings"),
                        hotel_phoneno=hotel_data.get("phoneno", ""),
                        hotel_website=hotel_data.get("website", ""),
                        hotel_location_id=Location.objects.filter(id=location_data.get("id")).first() if location_data.get("id") else None,
                        hotel_location_name=location_data.get("name", ""),
                        hotel_location_address=location_data.get("address", ""),
                        hotel_location_city=location_data.get("city", ""),
                        hotel_location_state=location_data.get("state", ""),
                        hotel_location_country=location_data.get("country", ""),
                        hotel_amenities=hotel_data.get("amenities", []),
                        hotel_inclusions=hotel_data.get("inclusions", []),
                        hotel_exclusions=hotel_data.get("exclusions", []),
                        hotel_policies=hotel_data.get("policies", []),
                        hotel_images=hotel_data.get("images", []),
                        room=room,
                        room_name=room_data.get("name", ""),
                        room_type=room_data.get("type", ""),
                        room_capacity=room_data.get("capacity"),
                        room_bedtype=room_data.get("bedtype", ""),
                        room_price_per_night=room_data.get("price_per_night"),
                        room_amenities=room_data.get("amenities", []),
                        room_inclusions=room_data.get("inclusions", []),
                        room_exclusions=room_data.get("exclusions", []),
                        room_policies=room_data.get("policies", []),
                        room_images=room_data.get("images", []),
                        car_dealer=car_dealer,
                        car_dealer_name=car_dealer_data.get("dealer_name", ""),
                        car_dealer_contact=car_dealer_data.get("contact_no", ""),
                        car_dealer_location_city=car_dealer_data.get("location", {}).get("city", ""),
                        car_dealer_location_state=car_dealer_data.get("location", {}).get("state", ""),
                        car_dealer_location_country=car_dealer_data.get("location", {}).get("country", ""),
                        car_type=car_type,
                        car_type_name=car_dealer_transport_types[0].get("type", "") if car_dealer_transport_types else "",
                        car_type_capacity=car_dealer_transport_types[0].get("capacity") if car_dealer_transport_types else None,
                        car_dealer_transport_types=car_dealer_transport_types
                    )


                    # Process activities for this day
                    activities = day_detail.get("activities", [])
                    for activity in activities:
                        location_data = activity.get("location", {})

                        # Get location reference if ID is provided
                        location_id = None
                        if location_data.get("id"):
                            location_id = Location.objects.filter(id=location_data["id"]).first()

                        TransactionItineraryDetails.objects.create(
                            transaction_day=day_instance,
                            activity_type=activity.get("type", ""),
                            activity_name=activity.get("name", ""),
                            activity_description=activity.get("description", ""),
                            contact_no=activity.get("contact_no", ""),
                            charges=float(activity.get("charges", 0)),
                            sequence=activity.get("sequence", 0),
                            itinerary_item_id=activity.get("itinerary_item_id"),
                            location_id=location_id,
                            location_city=location_data.get("city", ""),
                            location_state=location_data.get("state", ""),
                            location_name=location_data.get("name", ""),
                            location_address=location_data.get("address", ""),
                            location_country=location_data.get("country", ""),
                            location_pin_code=location_data.get("pin_code", ""),
                            location_lat=location_data.get("lat", ""),
                            location_lng=location_data.get("lng", ""),
                            location_tour_operator_id=location_data.get("tour_operator_id"),
                            location_created_by_id=location_data.get("created_by_id"),
                            activity_images=activity.get("images", [])
                        )

                      
                # Success response with transaction ID
                return JsonResponse({
                    "message": "Transaction created successfully",
                    "transaction_id": transaction_instance.id
                }, status=201)

        except Customer.DoesNotExist:
            return JsonResponse({"error": "Customer not found or unauthorized for the specified tour operator"}, status=404)
        except Package.DoesNotExist:
            return JsonResponse({"error": "Package not found or unauthorized for the specified tour operator"}, status=404)
        except Destination.DoesNotExist:
            return JsonResponse({"error": "Destination not found or unauthorized for the specified tour operator"}, status=404)
        except Hotel.DoesNotExist:
            return JsonResponse({"error": "Hotel not found or unauthorized for the specified tour operator"}, status=404)
        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found in specified hotel"}, status=404)
        except Cardealer.DoesNotExist:
            return JsonResponse({"error": "Car dealer not found or unauthorized for the specified tour operator"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
def get_transaction(request):
    """
    DEPRECATED: This function uses the old Transaction model structure.
    Please use the new transaction API that works with Leads.
    """
    return JsonResponse({
        "error": "This API is deprecated. Please use the new Lead-based transaction workflow.",
        "message": "Transaction model has been updated to work with Leads. See documentation for migration guide.",
        "documentation": "docs/transaction_api_update_for_ui.md"
    }, status=410)

def get_transaction_old(request):
    """
    OLD IMPLEMENTATION - Kept for reference only
    Get a transaction with complete package snapshot.
    Returns the same structure as package API response.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        transaction_id = data.get('transaction_id')

        try:
            transaction = Transaction.objects.get(id=transaction_id)

            # Build package snapshot structure matching package API response
            package_snapshot = {
                "id": transaction.package.id if transaction.package else None,
                "name": transaction.package_name,
                "destination_id": transaction.destination.id if transaction.destination else None,
                "description": transaction.package_description,
                "pax_size": transaction.pax_size,
                "contains_travel_fare": transaction.contains_travel_fare,
                "transport_type": transaction.transport_type,
                "no_of_days": transaction.no_of_days,
                "package_amount": float(transaction.package_amount),
                "is_active": True,
                "type": transaction.package_type,
                "terms_and_conditions": "",
                "inclusions": transaction.package_inclusions or [],
                "exclusions": transaction.package_exclusions or [],
                "images": transaction.package_images or [],
                "itinerary_details": []
            }

            # Build transaction-specific data
            response_data = {
                "transaction_id": transaction.id,
                "customer_id": transaction.customer.id,
                "created_by": transaction.created_by.id,
                "tour_operator": transaction.tour_operator.id,
                "proposed_package_amount": float(transaction.proposed_package_amount),
                "original_package_amount": float(transaction.original_package_amount),
                "discount_amount": float(transaction.discount_amount),
                "margin_of_profit": float(transaction.margin_of_profit),
                "taxes": float(transaction.taxes),
                "final_amount": float(transaction.final_amount),
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "package_snapshot": package_snapshot
            }

            # Iterating over each day in transaction day details
            for day_detail in transaction.day_details.all().order_by('day'):
                # Build hotel details with complete snapshot
                hotel_data = {
                    "id": day_detail.hotel.id if day_detail.hotel else None,
                    "name": day_detail.hotel_name,
                    "description": day_detail.hotel_description,
                    "ratings": float(day_detail.hotel_ratings) if day_detail.hotel_ratings else None,
                    "phoneno": day_detail.hotel_phoneno,
                    "website": day_detail.hotel_website,
                    "location": {
                        "id": day_detail.hotel_location_id.id if day_detail.hotel_location_id else None,
                        "name": day_detail.hotel_location_name,
                        "address": day_detail.hotel_location_address,
                        "city": day_detail.hotel_location_city,
                        "state": day_detail.hotel_location_state,
                        "country": day_detail.hotel_location_country
                    },
                    "amenities": day_detail.hotel_amenities or [],
                    "inclusions": day_detail.hotel_inclusions or [],
                    "exclusions": day_detail.hotel_exclusions or [],
                    "policies": day_detail.hotel_policies or [],
                    "images": day_detail.hotel_images or [],
                    "rooms": [{
                        "id": day_detail.room.id if day_detail.room else None,
                        "name": day_detail.room_name,
                        "type": day_detail.room_type,
                        "capacity": day_detail.room_capacity,
                        "bedtype": day_detail.room_bedtype,
                        "price_per_night": float(day_detail.room_price_per_night) if day_detail.room_price_per_night else None,
                        "amenities": day_detail.room_amenities or [],
                        "inclusions": day_detail.room_inclusions or [],
                        "exclusions": day_detail.room_exclusions or [],
                        "policies": day_detail.room_policies or [],
                        "images": day_detail.room_images or []
                    }]
                }

                # Build car dealer details
                car_dealer_data = {
                    "id": day_detail.car_dealer.id if day_detail.car_dealer else None,
                    "dealer_name": day_detail.car_dealer_name,
                    "contact_no": day_detail.car_dealer_contact,
                    "location": {
                        "city": day_detail.car_dealer_location_city,
                        "state": day_detail.car_dealer_location_state,
                        "country": day_detail.car_dealer_location_country
                    },
                    "transport_types": day_detail.car_dealer_transport_types or []
                }

                # Build day info matching package API structure
                day_info = {
                    "day": day_detail.day,
                    "city": day_detail.city,
                    "state": day_detail.state,
                    "title": day_detail.title,
                    "description": day_detail.description,
                    "note": day_detail.note,
                    "hotel_details": [hotel_data],  # Return as list to match package API
                    "car_dealers": [car_dealer_data],  # Return as list to match package API
                    "activities": []
                }

                # Iterating over each itinerary detail in the day
                for itinerary in day_detail.itinerary_details.all().order_by('sequence'):
                    activity_info = {
                        "name": itinerary.activity_name,
                        "type": itinerary.activity_type,
                        "description": itinerary.activity_description,
                        "charges": float(itinerary.charges) if itinerary.charges else 0.0,
                        "contact_no": itinerary.contact_no,
                        "sequence": itinerary.sequence or 0,
                        "itinerary_item_id": itinerary.itinerary_item_id,
                        "location": {
                            "id": itinerary.location_id.id if itinerary.location_id else None,
                            "tour_operator_id": itinerary.location_tour_operator_id,
                            "created_by_id": itinerary.location_created_by_id,
                            "city": itinerary.location_city,
                            "state": itinerary.location_state,
                            "country": itinerary.location_country,
                            "pin_code": itinerary.location_pin_code,
                            "name": itinerary.location_name,
                            "address": itinerary.location_address,
                            "lat": itinerary.location_lat,
                            "lng": itinerary.location_lng
                        },
                        "images": itinerary.activity_images or []
                    }
                    day_info["activities"].append(activity_info)

                package_snapshot["itinerary_details"].append(day_info)

            return JsonResponse(response_data, safe=False, status=200)

        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        

def update_transaction(request):
    """
    DEPRECATED: This function uses the old Transaction model structure.
    Please use the new transaction API that works with Leads.
    """
    return JsonResponse({
        "error": "This API is deprecated. Please use the new Lead-based transaction workflow.",
        "message": "Transaction model has been updated to work with Leads. See documentation for migration guide.",
        "documentation": "docs/transaction_api_update_for_ui.md"
    }, status=410)

def update_transaction_old(request):
    """
    OLD IMPLEMENTATION - Kept for reference only
    Update a transaction with complete or partial package snapshot.
    Accepts the same structure as add_transaction and allows updating any field.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        required_fields = ["transaction_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Get existing transaction
                transaction_instance = Transaction.objects.get(id=data['transaction_id'])

                # Update customer, created_by, tour_operator if provided
                if data.get('customer_id'):
                    customer = Customer.objects.get(id=data['customer_id'])
                    transaction_instance.customer = customer

                if data.get('created_by'):
                    created_by = User.objects.get(id=data['created_by'])
                    transaction_instance.created_by = created_by

                if data.get('tour_operator'):
                    tour_operator = Touroperator.objects.get(id=data['tour_operator'])
                    transaction_instance.tour_operator = tour_operator

                # Update transaction-specific fields
                if 'proposed_package_amount' in data:
                    transaction_instance.proposed_package_amount = data['proposed_package_amount']
                if 'original_package_amount' in data:
                    transaction_instance.original_package_amount = data['original_package_amount']
                if 'discount_amount' in data:
                    transaction_instance.discount_amount = data['discount_amount']
                if 'margin_of_profit' in data:
                    transaction_instance.margin_of_profit = data['margin_of_profit']
                if 'taxes' in data:
                    transaction_instance.taxes = data['taxes']
                if 'final_amount' in data:
                    transaction_instance.final_amount = data['final_amount']

                # Update package snapshot if provided
                if 'package_snapshot' in data:
                    pkg_snapshot = data['package_snapshot']

                    # Update package and destination references if IDs changed
                    if pkg_snapshot.get('id') and (not transaction_instance.package or transaction_instance.package.id != pkg_snapshot['id']):
                        package = Package.objects.filter(id=pkg_snapshot['id']).first()
                        transaction_instance.package = package

                    if pkg_snapshot.get('destination_id') and (not transaction_instance.destination or transaction_instance.destination.id != pkg_snapshot['destination_id']):
                        destination = Destination.objects.filter(id=pkg_snapshot['destination_id']).first()
                        transaction_instance.destination = destination

                    # Update package snapshot fields
                    if 'name' in pkg_snapshot:
                        transaction_instance.package_name = pkg_snapshot['name']
                    if 'description' in pkg_snapshot:
                        transaction_instance.package_description = pkg_snapshot['description']
                    if 'type' in pkg_snapshot:
                        transaction_instance.package_type = pkg_snapshot['type']
                    if 'pax_size' in pkg_snapshot:
                        transaction_instance.pax_size = pkg_snapshot['pax_size']
                    if 'contains_travel_fare' in pkg_snapshot:
                        transaction_instance.contains_travel_fare = pkg_snapshot['contains_travel_fare']
                    if 'transport_type' in pkg_snapshot:
                        transaction_instance.transport_type = pkg_snapshot['transport_type']
                    if 'no_of_days' in pkg_snapshot:
                        transaction_instance.no_of_days = pkg_snapshot['no_of_days']
                    if 'package_amount' in pkg_snapshot:
                        transaction_instance.package_amount = pkg_snapshot['package_amount']
                    if 'inclusions' in pkg_snapshot:
                        transaction_instance.package_inclusions = pkg_snapshot['inclusions']
                    if 'exclusions' in pkg_snapshot:
                        transaction_instance.package_exclusions = pkg_snapshot['exclusions']
                    if 'images' in pkg_snapshot:
                        transaction_instance.package_images = pkg_snapshot['images']

                # Save updated transaction
                transaction_instance.save()

                # Update itinerary details if provided
                if 'package_snapshot' in data and 'itinerary_details' in data['package_snapshot']:
                    # Clear existing day details and itinerary details
                    TransactionItineraryDetails.objects.filter(transaction_day__transaction=transaction_instance).delete()
                    TransactionDayDetails.objects.filter(transaction=transaction_instance).delete()

                    pkg_snapshot = data['package_snapshot']

                    # Process each day in itinerary_details from package snapshot (same logic as add_transaction)
                    for day_detail in pkg_snapshot.get("itinerary_details", []):
                        day = day_detail.get("day")

                        # Get day-wise metadata
                        city = day_detail.get("city", "")
                        state = day_detail.get("state", "")
                        title = day_detail.get("title", "")
                        description = day_detail.get("description", "")
                        note = day_detail.get("note", "")

                        # Process hotel details
                        hotel_details_list = day_detail.get("hotel_details", [])
                        if not hotel_details_list:
                            continue

                        selected_hotel_idx = day_detail.get("selected_hotel_index", 0)
                        hotel_data = hotel_details_list[selected_hotel_idx] if selected_hotel_idx < len(hotel_details_list) else hotel_details_list[0]

                        # Get hotel and room references
                        hotel = None
                        room = None
                        if hotel_data.get('id'):
                            hotel = Hotel.objects.filter(id=hotel_data['id']).first()

                        # Get selected room
                        room_data = hotel_data.get("room", {})
                        if isinstance(hotel_data.get("rooms"), list) and len(hotel_data.get("rooms", [])) > 0:
                            selected_room_idx = day_detail.get("selected_room_index", 0)
                            room_data = hotel_data["rooms"][selected_room_idx] if selected_room_idx < len(hotel_data["rooms"]) else hotel_data["rooms"][0]

                        if room_data.get('id'):
                            room = Room.objects.filter(id=room_data['id']).first()

                        # Process car dealer details
                        car_dealers_list = day_detail.get("car_dealers", [])
                        car_dealer = None
                        car_type = None
                        car_dealer_data = {}
                        car_dealer_transport_types = []

                        if car_dealers_list:
                            selected_dealer_idx = day_detail.get("selected_car_dealer_index", 0)
                            car_dealer_data = car_dealers_list[selected_dealer_idx] if selected_dealer_idx < len(car_dealers_list) else car_dealers_list[0]

                            if car_dealer_data.get('id'):
                                car_dealer = Cardealer.objects.filter(id=car_dealer_data['id']).first()

                            car_dealer_transport_types = car_dealer_data.get("transport_types", [])

                            if car_dealer_transport_types:
                                selected_transport_idx = day_detail.get("selected_transport_index", 0)
                                transport_data = car_dealer_transport_types[selected_transport_idx] if selected_transport_idx < len(car_dealer_transport_types) else car_dealer_transport_types[0]
                                if transport_data.get('type'):
                                    car_type = CarType.objects.filter(name=transport_data['type']).first()

                        location_data = hotel_data.get("location", {})

                        # Create TransactionDayDetails with complete snapshot
                        day_instance = TransactionDayDetails.objects.create(
                            transaction=transaction_instance,
                            day=day,
                            city=city,
                            state=state,
                            title=title,
                            description=description,
                            note=note,
                            hotel=hotel,
                            hotel_name=hotel_data.get("name", ""),
                            hotel_description=hotel_data.get("description", ""),
                            hotel_ratings=hotel_data.get("ratings"),
                            hotel_phoneno=hotel_data.get("phoneno", ""),
                            hotel_website=hotel_data.get("website", ""),
                            hotel_location_id=Location.objects.filter(id=location_data.get("id")).first() if location_data.get("id") else None,
                            hotel_location_name=location_data.get("name", ""),
                            hotel_location_address=location_data.get("address", ""),
                            hotel_location_city=location_data.get("city", ""),
                            hotel_location_state=location_data.get("state", ""),
                            hotel_location_country=location_data.get("country", ""),
                            hotel_amenities=hotel_data.get("amenities", []),
                            hotel_inclusions=hotel_data.get("inclusions", []),
                            hotel_exclusions=hotel_data.get("exclusions", []),
                            hotel_policies=hotel_data.get("policies", []),
                            hotel_images=hotel_data.get("images", []),
                            room=room,
                            room_name=room_data.get("name", ""),
                            room_type=room_data.get("type", ""),
                            room_capacity=room_data.get("capacity"),
                            room_bedtype=room_data.get("bedtype", ""),
                            room_price_per_night=room_data.get("price_per_night"),
                            room_amenities=room_data.get("amenities", []),
                            room_inclusions=room_data.get("inclusions", []),
                            room_exclusions=room_data.get("exclusions", []),
                            room_policies=room_data.get("policies", []),
                            room_images=room_data.get("images", []),
                            car_dealer=car_dealer,
                            car_dealer_name=car_dealer_data.get("dealer_name", ""),
                            car_dealer_contact=car_dealer_data.get("contact_no", ""),
                            car_dealer_location_city=car_dealer_data.get("location", {}).get("city", ""),
                            car_dealer_location_state=car_dealer_data.get("location", {}).get("state", ""),
                            car_dealer_location_country=car_dealer_data.get("location", {}).get("country", ""),
                            car_type=car_type,
                            car_type_name=car_dealer_transport_types[0].get("type", "") if car_dealer_transport_types else "",
                            car_type_capacity=car_dealer_transport_types[0].get("capacity") if car_dealer_transport_types else None,
                            car_dealer_transport_types=car_dealer_transport_types
                        )

                        # Process activities for this day
                        activities = day_detail.get("activities", [])
                        for activity in activities:
                            location_data = activity.get("location", {})

                            # Get location reference if ID is provided
                            location_id = None
                            if location_data.get("id"):
                                location_id = Location.objects.filter(id=location_data["id"]).first()

                            TransactionItineraryDetails.objects.create(
                                transaction_day=day_instance,
                                activity_type=activity.get("type", ""),
                                activity_name=activity.get("name", ""),
                                activity_description=activity.get("description", ""),
                                contact_no=activity.get("contact_no", ""),
                                charges=float(activity.get("charges", 0)),
                                sequence=activity.get("sequence", 0),
                                itinerary_item_id=activity.get("itinerary_item_id"),
                                location_id=location_id,
                                location_city=location_data.get("city", ""),
                                location_state=location_data.get("state", ""),
                                location_name=location_data.get("name", ""),
                                location_address=location_data.get("address", ""),
                                location_country=location_data.get("country", ""),
                                location_pin_code=location_data.get("pin_code", ""),
                                location_lat=location_data.get("lat", ""),
                                location_lng=location_data.get("lng", ""),
                                location_tour_operator_id=location_data.get("tour_operator_id"),
                                location_created_by_id=location_data.get("created_by_id"),
                                activity_images=activity.get("images", [])
                            )

                # Success response with transaction ID
                return JsonResponse({
                    "message": "Transaction updated successfully",
                    "transaction_id": transaction_instance.id
                }, status=200)

        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)
        except Customer.DoesNotExist:
            return JsonResponse({"error": "Customer not found"}, status=404)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Tour operator not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)