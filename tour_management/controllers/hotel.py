from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
import json
from ..models import User, Touroperator, Location, Hotel, Room, Amenity, Inclusion, Exclusion, Policy
from django.core.exceptions import ValidationError
from django.core import serializers
from django.http import JsonResponse
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ValidationError



def add_hotel(request):
    required_keys = ["name", "created_by", "location", "tour_operator_id", "rooms", "phoneno"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        if missing_keys:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_keys)}"}, status=400)

        try:
            with transaction.atomic():
                # Check for duplicate hotel based on phoneno
                if Hotel.objects.filter(phoneno=data['phoneno']).exists():
                    return JsonResponse({"error": "A hotel with this phone number already exists."}, status=409)

                # Fetch related objects
                touroperator = Touroperator.objects.get(id=data['tour_operator_id'])
                user = User.objects.get(id=data['created_by'])

                # Handle location (reuse if exists or create a new one)
                location_data = data['location']
                location, _ = Location.objects.get_or_create(
                    tour_operator=touroperator,
                    name=location_data['name'],
                    city=location_data['city'],
                    state=location_data['state'],
                    country=location_data['country'],
                    defaults={
                        'created_by': user,
                        'pin_code': location_data.get('country_code'),
                        'address': location_data.get('address'),
                        'lat': float(location_data.get('lat')),
                        'lng': float(location_data.get('lng'))
                    }
                )

                # Create the Hotel entry
                hotel = Hotel.objects.create(
                    tour_operator=touroperator,
                    created_by=user,
                    location=location,
                    name=data['name'],
                    description=data.get('description'),
                    ratings=data.get('ratings'),
                    website=data.get('website'),
                    phoneno=data['phoneno']
                )

                # Add shared items for the hotel with tour_operator and created_by
                hotel_amenities = add_shared_items(data.get("amenities", []), hotel.id, 'hotel', Amenity, touroperator, user)
                hotel_inclusions = add_shared_items(data.get("inclusions", []), hotel.id, 'hotel', Inclusion, touroperator, user)
                hotel_exclusions = add_shared_items(data.get("exclusions", []), hotel.id, 'hotel', Exclusion, touroperator, user)
                hotel_policies = add_shared_items(data.get("policies", []), hotel.id, 'hotel', Policy, touroperator, user)

                # Add rooms and associated shared items
                rooms_data = data['rooms']
                added_rooms = []
                for room_data in rooms_data:
                    room = Room.objects.create(
                        hotel=hotel,
                        tour_operator=touroperator,
                        created_by=user,
                        name=room_data.get('name'),
                        type=room_data['type'],
                        capacity=room_data.get('capacity'),
                        bedtype=room_data.get('bedtype'),
                        description=room_data.get('description'),
                        rating=room_data.get('rating'),
                        price_per_night=room_data.get('price_per_night')
                    )

                    # Add shared items for the room
                    room_amenities = add_shared_items(room_data.get("amenities", []), room.id, 'room', Amenity, touroperator, user)
                    room_inclusions = add_shared_items(room_data.get("inclusions", []), room.id, 'room', Inclusion, touroperator, user)
                    room_exclusions = add_shared_items(room_data.get("exclusions", []), room.id, 'room', Exclusion, touroperator, user)
                    room_policies = add_shared_items(room_data.get("policies", []), room.id, 'room', Policy, touroperator, user)

                    # Collect room data for response, including shared items
                    room_response = {
                        "id": room.id,
                        "name": room.name,
                        "type": room.type,
                        "capacity": room.capacity,
                        "bedtype": room.bedtype,
                        "description": room.description,
                        "rating": room.rating,
                        "price_per_night": room.price_per_night,
                        "amenities": room_amenities,
                        "inclusions": room_inclusions,
                        "exclusions": room_exclusions,
                        "policies": room_policies
                    }
                    added_rooms.append(room_response)

                # Prepare response data
                response_data = {
                    "id": hotel.id,
                    "name": hotel.name,
                    "description": hotel.description,
                    "ratings": hotel.ratings,
                    "website": hotel.website,
                    "phoneno": hotel.phoneno,
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "address": location.address,
                        "city": location.city,
                        "state": location.state,
                        "country": location.country,
                        "lat": float(location.lat),
                        "lng": float(location.lng)
                    },
                    "amenities": hotel_amenities,
                    "inclusions": hotel_inclusions,
                    "exclusions": hotel_exclusions,
                    "policies": hotel_policies,
                    "rooms": added_rooms
                }

            # Return success response
            return JsonResponse(response_data, status=201)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def add_shared_items(items_data, type_id, item_type, model, touroperator, user):
    """Helper function to add shared items with tour_operator and created_by fields."""
    added_items = []
    for item in items_data:
        shared_item = model.objects.create(
            name=item['name'],
            description=item.get('description', ''),
            type=item_type,
            type_id=type_id,
            tour_operator=touroperator,
            created_by=user
        )
        added_items.append({
            "id": shared_item.id,
            "name": shared_item.name,
            "description": shared_item.description
        })
    return added_items

def update_hotel(request):
    required_keys = ["id", "name", "created_by", "location", "tour_operator_id", "rooms", "phoneno"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        if missing_keys:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_keys)}"}, status=400)

        try:
            with transaction.atomic():
                # Fetch the hotel and related objects
                hotel = Hotel.objects.select_related('location').filter(
                    id=data['id'], tour_operator_id=data['tour_operator_id']
                ).first()

                if hotel is None:
                    return JsonResponse({"error": "Hotel with the given ID and tour operator does not exist."}, status=404)

                # Check if another hotel with the same phoneno exists
                if Hotel.objects.filter(phoneno=data['phoneno']).exclude(id=hotel.id).exists():
                    return JsonResponse({"error": "A hotel with this phone number already exists."}, status=409)

                # Fetch tour_operator and user for shared items
                touroperator = Touroperator.objects.get(id=data['tour_operator_id'])
                user = User.objects.get(id=data['created_by'])

                # Update or reuse existing location
                location_data = data['location']
                location, _ = Location.objects.get_or_create(
                    tour_operator_id=data['tour_operator_id'],
                    name=location_data['name'],
                    city=location_data['city'],
                    state=location_data['state'],
                    country=location_data['country'],
                    defaults={
                        'created_by': user                      
                    }
                )
                # If location already exists, update it if necessary
                #if not location:
                location.pin_code = location_data.get('country_code', location.pin_code)
                location.address = location_data.get('address', location.address)
                location.lat = float(location_data.get('lat', location.lat))
                location.lng = float(location_data.get('lng', location.lng))
                location.save()

                # Update Hotel details
                hotel.location = location
                hotel.name = data['name']
                hotel.description = data.get('description', hotel.description)
                hotel.ratings = data.get('ratings', hotel.ratings)
                hotel.website = data.get('website', hotel.website)
                hotel.phoneno = data['phoneno']
                hotel.save()

                # Update shared items for the hotel
                hotel_amenities = update_shared_items(data.get("amenities", []), hotel.id, 'hotel', Amenity, touroperator, user)
                hotel_inclusions = update_shared_items(data.get("inclusions", []), hotel.id, 'hotel', Inclusion, touroperator, user)
                hotel_exclusions = update_shared_items(data.get("exclusions", []), hotel.id, 'hotel', Exclusion, touroperator, user)
                hotel_policies = update_shared_items(data.get("policies", []), hotel.id, 'hotel', Policy, touroperator, user)

                # Update Rooms and associated shared items
                rooms_data = data['rooms']
                existing_room_ids = set()
                updated_rooms = []
                for room_data in rooms_data:
                    room_id = room_data.get("id")
                    if room_id:
                        # Update existing room if it exists
                        room = Room.objects.filter(id=room_id, hotel=hotel).first()
                        if room:
                            room.type = room_data['type']
                            room.capacity = room_data.get('capacity', room.capacity)
                            room.bedtype = room_data.get('bedtype', room.bedtype)
                            room.description = room_data.get('description', room.description)
                            room.rating = room_data.get('rating', room.rating)
                            room.price_per_night = room_data.get('price_per_night', room.price_per_night)
                            room.save()
                            existing_room_ids.add(room_id)
                        else:
                            # Create new room if ID doesn't exist
                            room = Room.objects.create(
                                hotel=hotel,
                                tour_operator=hotel.tour_operator,
                                created_by=hotel.created_by,
                                name=room_data.get('name'),
                                type=room_data['type'],
                                capacity=room_data.get('capacity'),
                                bedtype=room_data.get('bedtype'),
                                description=room_data.get('description'),
                                rating=room_data.get('rating'),
                                price_per_night=room_data.get('price_per_night')
                            )
                            existing_room_ids.add(room.id)
                    else:
                        # Create new room if no ID is provided
                        room = Room.objects.create(
                            hotel=hotel,
                            tour_operator=hotel.tour_operator,
                            created_by=hotel.created_by,
                            name=room_data.get('name'),
                            type=room_data['type'],
                            capacity=room_data.get('capacity'),
                            bedtype=room_data.get('bedtype'),
                            description=room_data.get('description'),
                            rating=room_data.get('rating'),
                            price_per_night=room_data.get('price_per_night')
                        )
                        existing_room_ids.add(room.id)

                    # Update shared items for the room
                    room_amenities = update_shared_items(room_data.get("amenities", []), room.id, 'room', Amenity, touroperator, user)
                    room_inclusions = update_shared_items(room_data.get("inclusions", []), room.id, 'room', Inclusion, touroperator, user)
                    room_exclusions = update_shared_items(room_data.get("exclusions", []), room.id, 'room', Exclusion, touroperator, user)
                    room_policies = update_shared_items(room_data.get("policies", []), room.id, 'room', Policy, touroperator, user)

                    # Collect room details for response
                    updated_rooms.append({
                        "id": room.id,
                        "name": room.name,
                        "type": room.type,
                        "capacity": room.capacity,
                        "bedtype": room.bedtype,
                        "description": room.description,
                        "rating": room.rating,
                        "price_per_night": room.price_per_night,
                        "amenities": room_amenities,
                        "inclusions": room_inclusions,
                        "exclusions": room_exclusions,
                        "policies": room_policies
                    })

                # Remove rooms that are no longer in the request data
                Room.objects.filter(hotel=hotel).exclude(id__in=existing_room_ids).delete()

                # Prepare response data
                response_data = {
                    "id": hotel.id,
                    "name": hotel.name,
                    "description": hotel.description,
                    "ratings": hotel.ratings,
                    "website": hotel.website,
                    "phoneno": hotel.phoneno,
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "address": location.address,
                        "city": location.city,
                        "state": location.state,
                        "country": location.country,
                        "lat": float(location.lat),
                        "lng": float(location.lng)
                    },
                    "amenities": hotel_amenities,
                    "inclusions": hotel_inclusions,
                    "exclusions": hotel_exclusions,
                    "policies": hotel_policies,
                    "rooms": updated_rooms
                }

            # Return success response
            return JsonResponse(response_data, status=200)

        except Touroperator.DoesNotExist:
            return JsonResponse({"error": "Invalid tour operator ID"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid user ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def update_shared_items(items_data, type_id, item_type, model, tour_operator, created_by):
    """Helper function to update shared items (amenities, inclusions, exclusions, policies) with tour_operator and created_by."""
    existing_item_ids = set()
    added_items = []
    for item in items_data:
        item_id = item.get("id")
        if item_id:
            shared_item = model.objects.filter(id=item_id, type=item_type, type_id=type_id).first()
            if shared_item:
                shared_item.name = item['name']
                shared_item.description = item.get('description', shared_item.description)
                shared_item.tour_operator = tour_operator
                shared_item.created_by = created_by
                shared_item.save()
                existing_item_ids.add(shared_item.id)
            else:
                shared_item = model.objects.create(
                    name=item['name'],
                    description=item.get('description', ''),
                    type=item_type,
                    type_id=type_id,
                    tour_operator=tour_operator,
                    created_by=created_by
                )
                existing_item_ids.add(shared_item.id)
        else:
            shared_item = model.objects.create(
                name=item['name'],
                description=item.get('description', ''),
                type=item_type,
                type_id=type_id,
                tour_operator=tour_operator,
                created_by=created_by
            )
            existing_item_ids.add(shared_item.id)

        added_items.append({
            "id": shared_item.id,
            "name": shared_item.name,
            "description": shared_item.description})

    # Remove items no longer in request data
    model.objects.filter(type=item_type, type_id=type_id).exclude(id__in=existing_item_ids).delete()
    return added_items


def add_rooms(request):
    required_keys = [ "created_by", "hotel_id", "tour_operator_id", "rooms"]

    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        missing_keys = set(required_keys) - data.keys()
        # Check for missing keys
        if missing_keys:
            raise ValidationError(
                ",".join(missing_keys)+" are required fields.")
        
        rooms = add_rooms_in_db(data['rooms'],data['hotel_id'],data['created_by'], data['tour_operator_id'])
        return HttpResponse(json.dumps(rooms),content_type='application/json')

def add_rooms_in_db(rooms,hotel_id,user_id,tour_operator_id):
    touroperator = Touroperator.objects.filter(id = tour_operator_id)[0]
    hotel = Hotel.objects.filter(id = hotel_id)[0]
    user = User.objects.filter(id = user_id)[0]
    added_rooms = []
    for room in rooms:
        room = Room(name=room['name'],
                    type=room['type'],
                    description=room['description'],
                    rating=room['rating'],
                    price_per_night=room['price_per_night'],
                    created_by=user,
                    hotel=hotel,
                    tour_operator=touroperator
                    )
        room.save()
        added_rooms.append( json.loads(serializers.serialize('json', [room],))[0])
    return added_rooms

def get_hotels_from_db(hotel_id):
    amenities = Amenity.objects.filter(type="hotel",type_id=hotel_id).all()
    inclusions = Inclusion.objects.filter(type="hotel",type_id=hotel_id).all()
    exclusions = Exclusion.objects.filter(type="hotel",type_id=hotel_id).all()
    policies = Policy.objects.filter(type="hotel",type_id=hotel_id).all()

    amenities_data = []
    for amenity in amenities:
        amenities_data.append({"id":amenity.id,"name":amenity.name,"description":amenity.description})
    
    inclusions_data = []
    for inclusion in inclusions:
        inclusions_data.append({"id":inclusion.id,"name":inclusion.name,"description":inclusion.description})
    
    
    exclusion_data = []
    for exclusion in exclusions:
        exclusion_data.append({"id":exclusion.id,"name":exclusion.name,"description":exclusion.description})
    
    
    policy_data = []
    for policy in policies:
        policy_data.append({"id":policy.id,"name":policy.name,"description":policy.description})

    hotel = Hotel.objects.filter(id =hotel_id).first()
    hotel_data = {
        "id": hotel.id,
        "name": hotel.name,
        "description": hotel.description,
        "ratings": float(hotel.ratings),
        "location": {
                "id": hotel.location.id,
                "name": hotel.location.name,
                "address": hotel.location.address,
                "city": hotel.location.city,
                "state": hotel.location.state,
                "country": hotel.location.country,
                "pin_code": hotel.location.pin_code,
                "created_by_id": hotel.location.created_by.id,
                "lat": float(hotel.location.lat),
                "lng": float(hotel.location.lng),
                "tour_operator_id": hotel.location.tour_operator.id,
            },
        "amenities":amenities_data,
        "inclusions":inclusions_data,
        "exclusions": exclusion_data,
        "policies":policy_data
    }
    rooms = get_rooms_from_db(hotel.id)
    hotel_data['rooms'] = rooms
    return hotel_data


def get_hotels(request):
    
    try:
        if request.method == 'POST':
            data = json.loads(request.body.decode("utf-8"))
            tour_operator_id = data["tour_operator_id"]
            city = None
            include_inactive = None
            if "city" in data:
                city = data['city']
            if "include_inactive" in data:
                include_inactive = data['include_inactive']
            else:
                include_inactive = False

            # Validate required tour_operator_id
            if not tour_operator_id:
                return JsonResponse({"error": "tour_operator_id is required."}, status=400)

            # Fetch hotels based on tour_operator_id and optional city filter
            hotels_query = Hotel.objects.filter(tour_operator_id=tour_operator_id)

            if not include_inactive:
                hotels_query = hotels_query.filter(is_active =True)
            if city:
                hotels_query = hotels_query.filter(location__city=city)

            # Prepare the response data
            hotels_data = []
            for hotel in hotels_query:
                # Fetch location
                location = hotel.location

                # Fetch shared items for hotel
                hotel_amenities = get_shared_items(hotel.id, 'hotel', Amenity)
                hotel_inclusions = get_shared_items(hotel.id, 'hotel', Inclusion)
                hotel_exclusions = get_shared_items(hotel.id, 'hotel', Exclusion)
                hotel_policies = get_shared_items(hotel.id, 'hotel', Policy)

                # Fetch rooms and their shared items
                rooms_data = []
                rooms = Room.objects.filter(hotel=hotel)
                for room in rooms:
                    room_amenities = get_shared_items(room.id, 'room', Amenity)
                    room_inclusions = get_shared_items(room.id, 'room', Inclusion)
                    room_exclusions = get_shared_items(room.id, 'room', Exclusion)
                    room_policies = get_shared_items(room.id, 'room', Policy)

                    # Prepare room data
                    room_data = {
                        "id": room.id,
                        "name": room.name,
                        "type": room.type,
                        "capacity": int(room.capacity),
                        "bedtype": room.bedtype,
                        "description": room.description,
                        "rating": int(room.rating),
                        "price_per_night": room.price_per_night,
                        "amenities": room_amenities,
                        "inclusions": room_inclusions,
                        "exclusions": room_exclusions,
                        "policies": room_policies
                    }
                    rooms_data.append(room_data)

                # Prepare hotel data
                hotel_data = {
                    "id": hotel.id,
                    "name": hotel.name,
                    "description": hotel.description,
                    "ratings": int(hotel.ratings),
                    "website": hotel.website,
                    "phoneno": hotel.phoneno,
                    "location": {
                        "id": location.id,
                        "name": location.name,
                        "address": location.address,
                        "city": location.city,
                        "state": location.state,
                        "country": location.country,
                        "lat": float(location.lat),
                        "lng": float(location.lng),
                    },
                    "amenities": hotel_amenities,
                    "inclusions": hotel_inclusions,
                    "exclusions": hotel_exclusions,
                    "policies": hotel_policies,
                    "rooms": rooms_data
                }
                hotels_data.append(hotel_data)

        # Return success response
        return HttpResponse(json.dumps({"code":200,"data":hotels_data}),content_type='application/json')


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_hotel_by_id(hotel_id):
    
    try:
       

        # Fetch hotels based on tour_operator_id and optional city filter
        hotel = Hotel.objects.filter(id=hotel_id).first()

        # Fetch location
        location = hotel.location

        # Fetch shared items for hotel
        hotel_amenities = get_shared_items(hotel.id, 'hotel', Amenity)
        hotel_inclusions = get_shared_items(hotel.id, 'hotel', Inclusion)
        hotel_exclusions = get_shared_items(hotel.id, 'hotel', Exclusion)
        hotel_policies = get_shared_items(hotel.id, 'hotel', Policy)

        # Fetch rooms and their shared items
        rooms_data = []
        rooms = Room.objects.filter(hotel=hotel)
        for room in rooms:
            room_amenities = get_shared_items(room.id, 'room', Amenity)
            room_inclusions = get_shared_items(room.id, 'room', Inclusion)
            room_exclusions = get_shared_items(room.id, 'room', Exclusion)
            room_policies = get_shared_items(room.id, 'room', Policy)

            # Prepare room data
            room_data = {
                "id": room.id,
                "name": room.name,
                "type": room.type,
                "capacity": room.capacity,
                "bedtype": room.bedtype,
                "description": room.description,
                "rating": room.rating,
                "price_per_night": room.price_per_night,
                "amenities": room_amenities,
                "inclusions": room_inclusions,
                "exclusions": room_exclusions,
                "policies": room_policies
            }
            rooms_data.append(room_data)

        # Prepare hotel data
        hotel_data = {
            "id": hotel.id,
            "name": hotel.name,
            "description": hotel.description,
            "ratings": hotel.ratings,
            "website": hotel.website,
            "phoneno": hotel.phoneno,
            "location": {
                "id": location.id,
                "name": location.name,
                "address": location.address,
                "city": location.city,
                "state": location.state,
                "country": location.country,
                "lat": float(location.lat),
                "lng": float(location.lng),
            },
            "amenities": hotel_amenities,
            "inclusions": hotel_inclusions,
            "exclusions": hotel_exclusions,
            "policies": hotel_policies,
            "rooms": rooms_data
        }

        # Return success response
        return hotel_data

    except Exception as e:
        return {}
    
def get_shared_items(type_id, item_type, model):
    """Helper function to fetch shared items (amenities, inclusions, exclusions, policies) and return them."""
    items = model.objects.filter(type=item_type, type_id=type_id).values('id', 'name', 'description')
    return list(items)


def get_rooms(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        if 'hotel_id' not in data:
            raise ValidationError(
                            "hotel_id is required field.")
        hotel_id = data['hotel_id']
        rooms = get_rooms_from_db(hotel_id=hotel_id)
        return HttpResponse(json.dumps(rooms),content_type='application/json')
    

def get_rooms_from_db(hotel_id):
    rooms = []
    rooms_from_db= Room.objects.filter(hotel_id =hotel_id).all()
    for room_from_db in rooms_from_db:
        amenities = Amenity.objects.filter(type="room",type_id=room_from_db.id).all()
        inclusions = Inclusion.objects.filter(type="room",type_id=room_from_db.id).all()
        exclusions = Exclusion.objects.filter(type="room",type_id=room_from_db.id).all()
        policies = Policy.objects.filter(type="room",type_id=room_from_db.id).all()

        amenities_data = []
        for amenity in amenities:
            amenities_data.append({"id":amenity.id,"name":amenity.name,"description":amenity.description})
        
        inclusions_data = []
        for inclusion in inclusions:
            inclusions_data.append({"id":inclusion.id,"name":inclusion.name,"description":inclusion.description})
        
        
        exclusion_data = []
        for exclusion in exclusions:
            exclusion_data.append({"id":exclusion.id,"name":exclusion.name,"description":exclusion.description})
        
        
        policy_data = []
        for policy in policies:
            policy_data.append({"id":policy.id,"name":policy.name,"description":policy.description})
        
        room_data = {
            "id":room_from_db.id,
            "type":room_from_db.type,
            "description":room_from_db.description,
            "price_per_night":float(room_from_db.price_per_night),
            "bedtype":room_from_db.bedtype,
            "capacity":int(room_from_db.capacity),
            "rating":float(room_from_db.rating),
            "amenities":amenities_data,
            "inclusions":inclusions_data,
            "exclusions": exclusion_data,
            "policies":policy_data

        }
        rooms.append(room_data)
    return rooms