
import os
import django
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import (
    User, Touroperator, Location, Hotel, Package, Destination,
    Itineraryitem, Packageitineraryitem, PackageOption, 
    PackageOptionHotelMapping, PackageHotelMapping
)

def create_rich_package():
    # 1. Get User and Tour Operator (Alina)
    try:
        user = User.objects.get(id=6)
        tour_operator = Touroperator.objects.get(id=6)
        print(f"Found User: {user.name} and TourOperator ID: {tour_operator.id}")
    except User.DoesNotExist:
        print("User 'Alina' (ID 6) not found. Please verify.")
        return

    # 2. Create Locations & Destinations
    # We will check if they exist first to avoid duplicates if run multiple times
    
    locations_data = [
        {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
        {"city": "Munnar", "state": "Kerala", "lat": 10.0889, "lng": 77.0595},
        {"city": "Thekkady", "state": "Kerala", "lat": 9.6031, "lng": 77.1615},
        {"city": "Alleppey", "state": "Kerala", "lat": 9.4981, "lng": 76.3388},
    ]

    loc_objs = {} # city -> Location object
    dest_objs = {} # city -> Destination object

    print("Creating/Fetching Locations and Destinations...")
    for loc in locations_data:
        # Create Location
        l_obj, created = Location.objects.get_or_create(
            name=loc['city'], # Using city as name for simplicity
            city=loc['city'],
            defaults={
                'state': loc['state'],
                'country': 'India',
                'lat': loc['lat'],
                'lng': loc['lng'],
                'tour_operator': tour_operator,
                'created_by': user
            }
        )
        loc_objs[loc['city']] = l_obj
        
        # Create Destination
        d_obj, created = Destination.objects.get_or_create(
            name=loc['city'],
            tour_operator_id=tour_operator,
            defaults={
                'created_by': user,
                'description': f"Beautiful destination of {loc['city']}"
            }
        )
        dest_objs[loc['city']] = d_obj

    # 3. Create Hotels (3 Tiers x 3 Locations - excluding Kochi for stay mostly, but let's add logic)
    # Itinerary: Munnar (2N), Thekkady (1N), Alleppey (1N)
    
    # Hotel Data Structure: City -> Tier -> Name
    hotels_info = {
        "Munnar": {
            "Standard": "Bellmount Resorts",
            "Deluxe": "Fragrant Nature",
            "Platinum": "Elixir Hills"
        },
        "Thekkady": {
            "Standard": "Abad Green Forest",
            "Deluxe": "Elephant Court",
            "Platinum": "Spice Village"
        },
        "Alleppey": {
            "Standard": "Private Deluxe Houseboat",
            "Deluxe": "Premium Houseboat",
            "Platinum": "Xandari Riverscapes Luxury Houseboat"
        }
    }

    hotel_objs = {} # City -> Tier -> HotelObject

    print("Creating Hotels...")
    for city, tiers in hotels_info.items():
        hotel_objs[city] = {}
        for tier, name in tiers.items():
            h_obj, created = Hotel.objects.get_or_create(
                name=name,
                location=loc_objs[city],
                tour_operator=tour_operator,
                defaults={
                    'created_by': user,
                    'description': f"{tier} class stay in {city}",
                    'ratings': 3 if tier == 'Standard' else 4 if tier == 'Deluxe' else 5
                }
            )
            hotel_objs[city][tier] = h_obj

    # 4. Create Package
    print("Creating Package...")
    pkg, created = Package.objects.get_or_create(
        name="Exotic Kerala 5-Day Experience",
        tour_operator=tour_operator,
        defaults={
            'created_by': user,
            'destination': dest_objs['Munnar'], # Primary destination
            'type': 'honeymoon',
            'no_of_days': 5,
            'pax_size': 2,
            'transport_type': 'Private Cab',
            'description': "Experience the misty hills of Munnar, wildlife to Thekkady, and serene backwaters of Alleppey."
        }
    )

    # 5. Create Itinerary Items and Link to Package
    # Day 1: Kochi -> Munnar
    # Day 2: Munnar Sightseeing
    # Day 3: Munnar -> Thekkady
    # Day 4: Thekkady -> Alleppey
    # Day 5: Alleppey -> Kochi
    
    itinerary_days = [
        {
            "day": 1,
            "title": "Arrival in Kochi & Transfer to Munnar",
            "desc": "Pick up from Kochi airport and drive to Munnar. Enroute visit Valara and Cheeyappara waterfalls.",
            "dest": dest_objs['Munnar']
        },
        {
            "day": 2,
            "title": "Munnar Sightseeing",
            "desc": "Visit Eravikulam National Park, Tea Museum, Mattupetty Dam, and Echo Point.",
            "dest": dest_objs['Munnar']
        },
        {
            "day": 3,
            "title": "Munnar to Thekkady",
            "desc": "Drive to Thekkady. Visit spice plantations and enjoy Periyar Lake boat safari.",
            "dest": dest_objs['Thekkady']
        },
        {
            "day": 4,
            "title": "Thekkady to Alleppey Houseboat",
            "desc": "Transfer to Alleppey. Check in to Houseboat for overnight cruise and stay.",
            "dest": dest_objs['Alleppey']
        },
        {
            "day": 5,
            "title": "Departure from Kochi",
            "desc": "Drive back to Kochi. Visit Fort Kochi if time permits. Drop at Airport.",
            "dest": dest_objs['Kochi']
        }
    ]

    print("Creating Itinerary...")
    # Clear existing mapping for this package if re-running
    Packageitineraryitem.objects.filter(package=pkg).delete()

    for item in itinerary_days:
        # Create generic Item
        it_item = Itineraryitem.objects.create(
            tour_operator_id=tour_operator,
            destination=item['dest'],
            city=item['dest'].name,
            item_type='Activity',
            description=item['title'] + ": " + item['desc'],
            created_by=user
        )
        
        # Link to Package
        Packageitineraryitem.objects.create(
            package=pkg,
            itinerary_item=it_item,
            created_by=user,
            day=item['day'],
            sequence=1,
            active=1
        )

    # 6. Create Package Options (Standard, Deluxe, Platinum)
    options_data = [
        {"name": "Standard", "price": 18000, "desc": "3-Star Hotels + AC Sedan"},
        {"name": "Deluxe", "price": 32000, "desc": "4-Star/Boutique Hotels + Executive Sedan"},
        {"name": "Platinum", "price": 65000, "desc": "5-Star Luxury Resorts + Innova Crysta"}
    ]

    print("Creating Package Options & Mappings...")
    # Clear existing options if re-running
    pkg.options.all().delete()
    # Also need to clear base package hotel mapping to avoid confusion, though usually that's for 'default'
    PackageHotelMapping.objects.filter(package=pkg).delete()

    for opt_data in options_data:
        tier = opt_data['name']
        option = PackageOption.objects.create(
            package=pkg,
            name=tier,
            amount=opt_data['price'],
            description=opt_data['desc'],
            tour_operator=tour_operator,
            created_by=user
        )

        # Map Hotels for this Option
        # Nights: Day 1 (Munnar), Day 2 (Munnar), Day 3 (Thekkady), Day 4 (Alleppey)
        
        # Night 1: Munnar
        PackageOptionHotelMapping.objects.create(
            package_option=option,
            hotel=hotel_objs['Munnar'][tier],
            day=1,
            tour_operator=tour_operator,
            selected_by=user
        )
        # Night 2: Munnar
        PackageOptionHotelMapping.objects.create(
            package_option=option,
            hotel=hotel_objs['Munnar'][tier],
            day=2,
            tour_operator=tour_operator,
            selected_by=user
        )
        # Night 3: Thekkady
        PackageOptionHotelMapping.objects.create(
            package_option=option,
            hotel=hotel_objs['Thekkady'][tier],
            day=3,
            tour_operator=tour_operator,
            selected_by=user
        )
        # Night 4: Alleppey
        PackageOptionHotelMapping.objects.create(
            package_option=option,
            hotel=hotel_objs['Alleppey'][tier],
            day=4,
            tour_operator=tour_operator,
            selected_by=user
        )

    print("SUCCESS: Rich Package created successfully!")
    print(f"Package ID: {pkg.id}")
    print(f"Package Name: {pkg.name}")
    print(f"Options Created: {[o.name for o in pkg.options.all()]}")

if __name__ == "__main__":
    create_rich_package()
