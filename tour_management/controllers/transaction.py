from django.db import transaction
from django.http import JsonResponse
from ..models import (
    Customer, Package, Destination, Touroperator, User, Location,
    Transaction, TransactionDayDetails, TransactionItineraryDetails, Event, SightSeeing,
     Inclusion, Exclusion, Amenity, Policy,Hotel, Cardealer, Room,CarType, Packageitineraryitem
)
import json
def add_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        required_fields = ["customer_id", "package_id", "destination_id", "created_by", "tour_operator"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Get and validate the main entities
                customer = Customer.objects.get(id=data['customer_id'], tour_operator=data['tour_operator'])
                package = Package.objects.get(id=data['package_id'], tour_operator=data['tour_operator'])
                destination = Destination.objects.get(id=data['destination_id'], tour_operator_id=data['tour_operator'])
                created_by = User.objects.get(id=data['created_by'])
                tour_operator = Touroperator.objects.get(id=data['tour_operator'])

                package_inclusions = [
                {"id": inc.id, "name": inc.name, "description": inc.description}
                for inc in Inclusion.objects.filter(type="package", type_id=package.id)
                ]
                package_exclusions = [
                    {"id": exc.id, "name": exc.name, "description": exc.description}
                    for exc in Exclusion.objects.filter(type="package", type_id=package.id)
                ]
                
                # Create the Transaction snapshot
                transaction_instance = Transaction.objects.create(
                    customer=customer,
                    package=package,
                    destination=destination,
                    created_by=created_by,
                    tour_operator=tour_operator,
                    package_name=package.name,
                    package_description=package.description,
                    package_type=data.get("package_type", ""),
                    pax_size=data.get("pax_size"),
                    contains_travel_fare=data.get("contains_travel_fare", False),
                    transport_type=data.get("transport_type", ""),
                    no_of_days=data.get("no_of_days", 0),
                    package_amount=data.get("package_amount", 0.0),
                    proposed_package_amount=data.get("proposed_package_amount", 0.0),
                    original_package_amount=data.get("original_package_amount", 0.0),
                    discount_amount=data.get("discount_amount", 0.0),
                    margin_of_profit=data.get("margin_of_profit", 0.0),
                    taxes=data.get("taxes", 0.0),
                    final_amount=data.get("final_amount", 0.0),
                    #package_amenities=package.amenities,  # From Package instance if available
                    package_inclusions=package_inclusions,
                    package_exclusions=package_exclusions,
                    #package_policies=package.policies
                )

                # Process each day in itinerary_details
                for day_detail in data.get("itinerary_details", []):
                    day = day_detail.get("day")

                    # Fetch hotel and room based on the provided IDs and validate tour_operator association
                    hotel = Hotel.objects.get(id=day_detail["hotel_details"]["hotel_id"], tour_operator=tour_operator)
                    room = Room.objects.get(id=day_detail["hotel_details"]["room_id"], hotel=hotel)

                    # Fetch car dealer and validate tour_operator association
                    car_dealer = Cardealer.objects.get(id=day_detail["car_dealers"]["car_dealer_id"], tour_operator=tour_operator)
                    car_type = CarType.objects.filter(name=day_detail["car_dealers"]["transport_name"]).first()
                    hotel_inclusions = [
                        {"id": inc.id, "name": inc.name, "description": inc.description}
                        for inc in Inclusion.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    hotel_exclusions = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Exclusion.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    hotel_amenities = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Amenity.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    hotel_policies = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Policy.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    

                    room_inclusions = [
                        {"id": inc.id, "name": inc.name, "description": inc.description}
                        for inc in Inclusion.objects.filter(type="room", type_id=room.id)
                        ]
                    room_exclusions = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Exclusion.objects.filter(type="room", type_id=room.id)
                        ]
                    room_amenities = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Amenity.objects.filter(type="room", type_id=room.id)
                        ]
                    room_policies = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Policy.objects.filter(type="room", type_id=room.id)
                        ]
                    
                    car_dealer_city=""
                    car_dealer_state=""
                    car_dealer_country=""
                    car_dealer_location = car_dealer.location
                    if car_dealer_location is not None:
                        car_dealer_city=car_dealer_location.city
                        car_dealer_state=car_dealer_location.state
                        car_dealer_country=car_dealer_location.country

                    # Create TransactionDayDetails for each day
                    day_instance = TransactionDayDetails.objects.create(
                        transaction=transaction_instance,
                        day=day,
                        hotel=hotel,
                        hotel_name=hotel.name,
                        hotel_description=hotel.description,
                        hotel_ratings=hotel.ratings,
                        hotel_phoneno=hotel.phoneno,
                        hotel_website=hotel.website,
                        hotel_location_id=hotel.location,
                        hotel_location_name=hotel.location.name,
                        hotel_location_address=hotel.location.address,
                        hotel_location_city=hotel.location.city,
                        hotel_location_state=hotel.location.state,
                        hotel_location_country=hotel.location.country,
                        hotel_amenities=hotel_amenities,  # Assuming amenities are directly related to Hotel
                        hotel_inclusions=hotel_inclusions,
                        hotel_exclusions=hotel_exclusions,
                        hotel_policies=hotel_policies,
                        room=room,
                        room_name=room.name,
                        room_type=room.type,
                        room_capacity=room.capacity,
                        room_bedtype=room.bedtype,
                        room_price_per_night=room.price_per_night,
                        room_amenities=room_amenities,
                        room_inclusions=room_inclusions,
                        room_exclusions=room_exclusions,
                        room_policies=room_policies,
                        car_dealer=car_dealer,
                        car_dealer_name=car_dealer.name,
                        car_dealer_contact=car_dealer.contact_no,
                        car_dealer_location_city =car_dealer_city,
                        car_dealer_location_state = car_dealer_state,
                        car_dealer_location_country = car_dealer_country,
                        car_type=car_type,
                        car_type_name=day_detail["car_dealers"]["transport_name"],
                        car_type_capacity=car_type.capacity if car_type else None
                    )


                
                    package_itinerary_items = Packageitineraryitem.objects.filter(
                        package=package.id, active=True,day = day_instance.day
                    )
                    for pii in package_itinerary_items:
                        itinerary = None
                        if pii.itinerary_item.item_type.lower() == 'event':
                            itinerary = Event.objects.filter(id=pii.itinerary_item.item_id).first()
                        elif pii.itinerary_item.item_type.lower() == 'sightseeing':
                            itinerary = SightSeeing.objects.filter(id=pii.itinerary_item.item_id).first()
                        location_id=None
                        location_city=""
                        location_state=""
                        location_country=""
                        location_name=""
                        location_address=""

                        if itinerary:
                            if itinerary.location is not None:
                                location_id = itinerary.location
                                location_city = itinerary.location.city
                                location_state = itinerary.location.state
                                location_country = itinerary.location.country
                                location_name = itinerary.location.name
                                location_address = itinerary.location.address

                            
                            TransactionItineraryDetails.objects.create(activity_type = pii.itinerary_item.item_type, 
                                                                    activity_name = itinerary.name,
                                                                    activity_description = itinerary.description,
                                                                    contact_no = itinerary.contact_no,
                                                                    charges = float(itinerary.charges or 0),
                                                                    location_id = location_id,
                                                                    location_city = location_city,
                                                                    location_state = location_state,
                                                                    location_name=location_name,
                                                                    location_address = location_address,
                                                                    location_country=location_country,
                                                                    transaction_day=day_instance
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
     if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        transaction_id = data.get('transaction_id')

        try:    
            transaction = Transaction.objects.get(id=transaction_id)

            # Collecting main transaction details
            response_data = {
                "customer_id": transaction.customer.id,
                "package_id": transaction.package.id,
                "destination_id": transaction.destination.id,
                "created_by": transaction.created_by.id,
                "tour_operator": transaction.tour_operator.id,
                "package_name": transaction.package_name,
                "package_description": transaction.package_description,
                "pax_size": transaction.pax_size,
                "contains_travel_fare": transaction.contains_travel_fare,
                "transport_type": transaction.transport_type,
                "no_of_days": transaction.no_of_days,
                "package_amount": float(transaction.package_amount),
                "package_type": transaction.package_type,
                "proposed_package_amount": float(transaction.proposed_package_amount),
                "original_package_amount": float(transaction.original_package_amount),
                "discount_amount": float(transaction.discount_amount),
                "margin_of_profit": float(transaction.margin_of_profit),
                "taxes": float(transaction.taxes),
                "final_amount": float(transaction.final_amount),
                "package_amenities": transaction.package_amenities,
                "package_inclusions": transaction.package_inclusions,
                "package_exclusions": transaction.package_exclusions,
                "package_policies": transaction.package_policies,
                "itinerary_details": [],
                "inclusions": transaction.package_inclusions,
                "exclusions": transaction.package_exclusions,
            }

            # Iterating over each day in transaction day details
            for day_detail in transaction.day_details.all():
                day_info = {
                    "day": day_detail.day,
                    "hotel_details": {
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
                        "amenities": day_detail.hotel_amenities,
                        "inclusions": day_detail.hotel_inclusions,
                        "exclusions": day_detail.hotel_exclusions,
                        "policies": day_detail.hotel_policies,
                        "room": {
                            "id": day_detail.room.id if day_detail.room else None,
                            "name": day_detail.room_name,
                            "type": day_detail.room_type,
                            "capacity": day_detail.room_capacity,
                            "bedtype": day_detail.room_bedtype,
                            "price_per_night": float(day_detail.room_price_per_night) if day_detail.room_price_per_night else None,
                            "amenities": day_detail.room_amenities,
                            "inclusions": day_detail.room_inclusions,
                            "exclusions": day_detail.room_exclusions,
                            "policies": day_detail.room_policies
                        }
                    },
                    "car_dealers": {
                        "id": day_detail.car_dealer.id if day_detail.car_dealer else None,
                        "dealer_name": day_detail.car_dealer_name,
                        "contact_no": day_detail.car_dealer_contact,
                        "transport_types": [
                            {"name": day_detail.car_type_name, "type": day_detail.car_type.name if day_detail.car_type else None}
                        ]
                    },
                    "activities": []
                }

                # Iterating over each itinerary detail in the day
                for itinerary in day_detail.itinerary_details.all():
                    activity_info = {
                        "name": itinerary.activity_name,
                        "type": itinerary.activity_type,
                        "description": itinerary.activity_description,
                        "charges": float(itinerary.charges) if itinerary.charges else 0.0,
                        "contact_no": itinerary.contact_no,
                        "location": {
                            "id": itinerary.location_id.id if itinerary.location_id else None,
                            "city": itinerary.location_city,
                            "state": itinerary.location_state,
                            "country": itinerary.location_country,
                            "name": itinerary.location_name,
                            "address": itinerary.location_address
                        }
                    }
                    day_info["activities"].append(activity_info)

                response_data["itinerary_details"].append(day_info)

            return JsonResponse(response_data, safe=False, status=200)

        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        

def update_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))

        required_fields = ["transaction_id", "customer_id", "package_id", "destination_id", "created_by", "tour_operator"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        try:
            with transaction.atomic():
                # Get and validate the main entities
                customer = Customer.objects.get(id=data['customer_id'], tour_operator=data['tour_operator'])
                package = Package.objects.get(id=data['package_id'], tour_operator=data['tour_operator'])
                destination = Destination.objects.get(id=data['destination_id'], tour_operator_id=data['tour_operator'])
                created_by = User.objects.get(id=data['created_by'])
                tour_operator = Touroperator.objects.get(id=data['tour_operator'])

                # Get existing transaction
                transaction_instance = Transaction.objects.get(id=data['transaction_id'])
                transaction_instance.customer = customer
                transaction_instance.package = package
                transaction_instance.destination = destination
                transaction_instance.created_by = created_by
                transaction_instance.tour_operator = tour_operator
                transaction_instance.package_type = data.get("package_type", "")
                transaction_instance.pax_size = data.get("pax_size")
                transaction_instance.contains_travel_fare = data.get("contains_travel_fare", False)
                transaction_instance.transport_type = data.get("transport_type", "")
                transaction_instance.no_of_days = data.get("no_of_days", 0)
                transaction_instance.package_amount = data.get("package_amount", 0.0)
                transaction_instance.proposed_package_amount = data.get("proposed_package_amount", 0.0)
                transaction_instance.original_package_amount = data.get("original_package_amount", 0.0)
                transaction_instance.discount_amount = data.get("discount_amount", 0.0)
                transaction_instance.margin_of_profit = data.get("margin_of_profit", 0.0)
                transaction_instance.taxes = data.get("taxes", 0.0)
                transaction_instance.final_amount = data.get("final_amount", 0.0)

                # Save updated transaction
                transaction_instance.save()

                # Clear existing day details and itinerary details
                TransactionItineraryDetails.objects.filter(transaction_day__transaction=transaction_instance).delete()
                TransactionDayDetails.objects.filter(transaction=transaction_instance).delete()

                # Process each day in itinerary_details
                for day_detail in data.get("itinerary_details", []):
                    day = day_detail.get("day")

                    # Fetch hotel and room based on the provided IDs and validate tour_operator association
                    hotel = Hotel.objects.get(id=day_detail["hotel_details"]["hotel_id"], tour_operator=tour_operator)
                    room = Room.objects.get(id=day_detail["hotel_details"]["room_id"], hotel=hotel)

                    # Fetch car dealer and validate tour_operator association
                    car_dealer = Cardealer.objects.get(id=day_detail["car_dealers"]["car_dealer_id"], tour_operator=tour_operator)
                    car_type = CarType.objects.filter(name=day_detail["car_dealers"]["transport_name"]).first()

                    # Create TransactionDayDetails for each day
                    hotel_inclusions = [
                        {"id": inc.id, "name": inc.name, "description": inc.description}
                        for inc in Inclusion.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    hotel_exclusions = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Exclusion.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    hotel_amenities = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Amenity.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    hotel_policies = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Policy.objects.filter(type="hotel", type_id=hotel.id)
                        ]
                    

                    room_inclusions = [
                        {"id": inc.id, "name": inc.name, "description": inc.description}
                        for inc in Inclusion.objects.filter(type="room", type_id=room.id)
                        ]
                    room_exclusions = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Exclusion.objects.filter(type="room", type_id=room.id)
                        ]
                    room_amenities = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Amenity.objects.filter(type="room", type_id=room.id)
                        ]
                    room_policies = [
                        {"id": exc.id, "name": exc.name, "description": exc.description}
                        for exc in Policy.objects.filter(type="room", type_id=room.id)
                        ]
                    day_instance = TransactionDayDetails.objects.create(
                        transaction=transaction_instance,
                        day=day,
                        hotel=hotel,
                        hotel_name=hotel.name,
                        hotel_description=hotel.description,
                        hotel_ratings=hotel.ratings,
                        hotel_phoneno=hotel.phoneno,
                        hotel_website=hotel.website,
                        hotel_location_id=hotel.location,
                        hotel_location_name=hotel.location.name,
                        hotel_location_address=hotel.location.address,
                        hotel_location_city=hotel.location.city,
                        hotel_location_state=hotel.location.state,
                        hotel_location_country=hotel.location.country,
                        hotel_amenities = hotel_amenities,
                        hotel_exclusions=hotel_exclusions,
                        hotel_policies =hotel_policies,
                        hotel_inclusions=hotel_inclusions,
                        room=room,
                        room_name=room.name,
                        room_type=room.type,
                        room_capacity=room.capacity,
                        room_bedtype=room.bedtype,
                        room_price_per_night=room.price_per_night,
                        room_amenities = room_amenities,
                        room_exclusions=room_exclusions,
                        room_policies =room_policies,
                        room_inclusions=room_inclusions,
                        car_dealer=car_dealer,
                        car_dealer_name=car_dealer.name,
                        car_dealer_contact=car_dealer.contact_no,
                        car_type=car_type,
                        car_type_name=day_detail["car_dealers"]["transport_name"],
                        car_type_capacity=car_type.capacity if car_type else None
                    )

                    # Fetch and add itinerary items
                    package_itinerary_items = Packageitineraryitem.objects.filter(
                        package=package.id, active=True, day=day_instance.day
                    )
                    for pii in package_itinerary_items:
                        itinerary = None
                        if pii.itinerary_item.item_type.lower() == 'event':
                            itinerary = Event.objects.filter(id=pii.itinerary_item.item_id).first()
                        elif pii.itinerary_item.item_type.lower() == 'sightseeing':
                            itinerary = SightSeeing.objects.filter(id=pii.itinerary_item.item_id).first()

                        if itinerary:
                            TransactionItineraryDetails.objects.create(
                                activity_type=pii.itinerary_item.item_type,
                                activity_name=itinerary.name,
                                activity_description=itinerary.description,
                                contact_no=itinerary.contact_no,
                                charges=float(itinerary.charges or 0),
                                location_id=itinerary.location,
                                location_city=itinerary.location.city if itinerary.location else "",
                                location_state=itinerary.location.state if itinerary.location else "",
                                location_country=itinerary.location.country if itinerary.location else "",
                                location_name=itinerary.location.name if itinerary.location else "",
                                location_address=itinerary.location.address if itinerary.location else "",
                                transaction_day=day_instance
                            )

                # Success response with transaction ID
                return JsonResponse({
                    "message": "Transaction updated successfully",
                    "transaction_id": transaction_instance.id
                }, status=200)

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