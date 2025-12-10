
import os
import sys
import django
import requests
import json
import decimal
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from PIL import Image
import io

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import (
    User, Touroperator, Package, Destination, Itineraryitem, Packageitineraryitem,
    PackageOption, PackageOptionHotelMapping, Hotel, Room, QuickHotel,
    ImageMetadata, Location, Inclusion, Exclusion, Policy, Amenity,
    DestinationPackageMapping
)

# Constants
API_BASE_URL = "https://tg.api.tourgenie.com/api"
IMAGE_BASE_URL = "https://tg.api.tourgenie.com/"

def get_input(prompt):
    if sys.version_info[0] < 3:
        return raw_input(prompt)
    return input(prompt)

def get_db_user():
    while True:
        username = get_input("Enter username to associate data with: ")
        try:
            user = User.objects.get(username=username)
            print("Found user: {}".format(user.name))
            if user.tour_operator_id:
                return user, user.tour_operator_id
            else:
                print("Error: User is not linked to a Tour Operator.")
                sys.exit(1)
        except User.DoesNotExist:
            print("User not found. Please try again.")

def download_image(url):
    print("Downloading image: {}".format(url))
    try:
        response = requests.get(url, stream=True, verify=False) # Disable SSL verify if needed, or fix certs
        if response.status_code == 200:
            content = response.content
            file_name = url.split("/")[-1]
            
            # Convert WebP (or others) to JPG
            try:
                image = Image.open(io.BytesIO(content))
                # Convert to RGB to handle RGBA (transparency in WebP/PNG)
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                    
                output_io = io.BytesIO()
                image.save(output_io, format='JPEG', quality=90)
                file_name = os.path.splitext(file_name)[0] + ".jpg"
                return ContentFile(output_io.getvalue(), name=file_name)
            except Exception as e:
                print("Image conversion failed for {}: {}, using original".format(url, e))
                return ContentFile(content, name=file_name)

    except Exception as e:
        print("Error downloading image {}: {}".format(url, e))
    return None

def create_image_metadata(image_file, user, tour_operator, module, record_id, description=""):
    if not image_file:
        return None
    
    try:
        img = ImageMetadata(
            tour_operator=tour_operator,
            module=module,
            record_id=record_id,
            description=description
        )
        img.image_path.save(image_file.name, image_file, save=True)
        return img.id
    except Exception as e:
        print("Error saving image metadata: {}".format(e))
        return None


def process_images(json_str, descriptor, user, tour_operator, module, record_id):
    """
    Parses image JSON string from API and saves images.
    Returns list of local image IDs.
    """
    if not json_str:
        return []
    
    try:
        data = json.loads(json_str)
        # Handle different structures
        image_paths = []
        if isinstance(data, dict):
            if 'images' in data:
                image_paths = data['images']
            elif 'image_paths' in data:
                image_paths = data['image_paths']
        elif isinstance(data, list):
            image_paths = data
        
        local_ids = []
        for path in image_paths:
            # Fix backslashes from API
            path = path.replace('\\', '/')
            full_url = urljoin(IMAGE_BASE_URL, path)
            image_file = download_image(full_url)
            if image_file:
                img_id = create_image_metadata(image_file, user, tour_operator, module, record_id, descriptor)
                if img_id:
                    local_ids.append(img_id)
        return local_ids

    except json.JSONDecodeError:
        print("Failed to decode image JSON")
        return []

def fetch_api_data(endpoint, method="GET", data=None):
    url = "{}/{}".format(API_BASE_URL, endpoint.lstrip('/'))
    # Fix backslashes in endpoint if any (unlikely but safe)
    url = url.replace('\\', '/')
    headers = {"Content-Type": "application/json"}
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers, verify=False)
        else:
            response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("API Request failed for {}: {}".format(url, e))
        return None




def import_hotels(user, tour_operator):
    print("\n=== Importing Hotels ===")
    
    # 1. Fetch Stays
    payload = {"budget_min_value": 0, "budget_max_value": 1000000}
    stays = fetch_api_data("Stay/GetStayList", "POST", payload)
    
    if not stays:
        print("No hotels found.")
        return

    print("Found {} hotels.".format(len(stays)))

    for stay in stays:
        stay_name = stay.get('stay_name')
        stay_id = stay.get('stay_id')
        print("Processing Hotel: {}".format(stay_name))
        
        # 1. Create/Get Location (Specific to this hotel)
        # Using hotel name as location name to ensure specificity, or just City? 
        # Given 'address' field in Location, it acts like a specific venue.
        loc_name = stay_name
        dest_city = stay.get('destination_name')
        dest_state = stay.get('state_name')
        address = stay.get('address')
        
        # Check if location already exists
        location = Location.objects.filter(name=loc_name, tour_operator=tour_operator).first()
        if not location:
            location = Location(
                name=loc_name,
                city=dest_city,
                state=dest_state,
                address=address,
                tour_operator=tour_operator,
                created_by=user
            )
            location.save()
            print("  Created Location: {}".format(loc_name))
            
        # 2. Create/Get Destination (Generic City/Region - optionally linked if needed elsewhere, but Hotel links to Location)
        # We also create a Destination for consistency if it doesn't exist, as it might be used in packages
        destination = Destination.objects.filter(name=dest_city, tour_operator_id=tour_operator).first()
        if not destination and dest_city:
            destination = Destination(
                name=dest_city, 
                tour_operator_id=tour_operator,
                created_by=user,
                description=f"Auto-imported from TourGenie Stay. State: {dest_state}"
            )
            destination.save()
            print("  Created Destination: {}".format(dest_city))
            
        # 3. Create/Update Hotel
        hotel = Hotel.objects.filter(name=stay_name, tour_operator_id=tour_operator).first()
        if not hotel:

            hotel = Hotel(
                name=stay_name,
                tour_operator=tour_operator,
                location=location, # Link to Location
                description=stay.get('stay_description'),
                # address field not in Hotel, it's in Location
                phoneno=stay.get('phone')[:15] if stay.get('phone') else None, 
                website=stay.get('web_link')[:45] if stay.get('web_link') else None,
                # email field not in Hotel model, ignoring
                ratings=stay.get('stay_rating') if stay.get('stay_rating') else 0, # field is ratings
                created_by=user
            )
            hotel.save()
            print("  Created Hotel: ID {}".format(hotel.id))
        else:
            print("  Hotel already exists, updating/skipping...")
            
        # Process Hotel Images
        # Hotels have 'images_desktop'
        image_ids = process_images(
            stay.get('images_desktop'),
            "Hotel Image",
            user,
            tour_operator,
            'hotel',
            hotel.id
        )
        if image_ids:
            # Hotel model has 'image_ids'
            hotel.image_ids = image_ids
            hotel.save()
            
        # Create Room
        room_type = stay.get('stay_room_type_name')
        if room_type:
            # Check if room exists for this hotel
            room = Room.objects.filter(hotel=hotel, name=room_type, tour_operator_id=tour_operator).first()


            if not room:
                room = Room(
                    hotel=hotel,
                    tour_operator=tour_operator,
                    name=room_type,
                    description=stay.get('meal_plan_name'), 
                    price_per_night=str(stay.get('base_rate_plus_traveler_markup')), 
                    created_by=user
                )
                room.save()
                print("  Created Room: {}".format(room_type))

def main():
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    user, tour_operator = get_db_user()
    
    # Import Hotels
    import_hotels(user, tour_operator)
    
    # 1. Get All Categories
    print("\n=== Fetching Package Categories ===")
    categories = fetch_api_data("activityandblogcategory/getactivityandblogcategory")
    
    if not categories:
        print("No categories found or failed to fetch.")
        return

    # Loop through each category
    for category in categories:
        category_id = category.get('activity_and_blog_category_id')
        category_name = category.get('activity_and_blog_category')
        
        if not category_id:
            continue
            
        print("\n=== Processing Category: {} (ID: {}) ===".format(category_name, category_id))
    
        # 2. Get Holiday List for this Category
        print("Fetching holiday list for category {}...".format(category_name))
        payload = {"budget_min_value": 0, "budget_max_value": 100000, "package_category_id": str(category_id)}
        holidays = fetch_api_data("Itinerary/GetHolidayList", "POST", payload)
        
        if not holidays:
            # print("No holidays found for category {}.".format(category_name))
            continue

        for pkg_summary in holidays:
            slug = pkg_summary.get('url_slug')
            if not slug:
                continue
                
            print("\nProcessing Package: {} ({})".format(pkg_summary.get('itinerary_name'), slug))
            
            # Check if package already exists
            existing_pkg = Package.objects.filter(name=pkg_summary.get('itinerary_name'), tour_operator=tour_operator).first()
            if existing_pkg:
                 print("Package '{0}' already exists. Deleting to re-import...".format(existing_pkg.name))
                 existing_pkg.delete()
            
            # 3. Get Full Details
            details_list = fetch_api_data("Itinerary/GetHolidayDetailsByHolidayName/{}".format(slug))
            if not details_list:
                continue
            details = details_list[0]
            
            # 4. Create/Get Destination
            # Using destination_name_to as the primary destination
            dest_name = details.get('destination_name_to')
            dest_state = details.get('state_name_to')
            
            # Create Destination if not exists
            # Destination requires tour_operator and name unique constraint
            destination = Destination.objects.filter(name=dest_name, tour_operator_id=tour_operator).first()
            if not destination:
                destination = Destination(
                    name=dest_name, 
                    tour_operator_id=tour_operator,
                    created_by=user,
                    description=f"Auto-imported from TourGenie. State: {dest_state}"
                )
                destination.save()
                print("Created Destination: {}".format(dest_name))
            
            # 5. Create Package
            pkg = Package(
                name=details.get('itinerary_name'),
                tour_operator=tour_operator,
                created_by=user,
                destination=destination,
                description=details.get('itinerary_description'),
                no_of_days=details.get('duration_in_days'),
                package_amount=details.get('base_price'), # Using base_price
                pax_size=details.get('adult'), # Assuming adult count as pax size for the quote? Or just default.
                type='group', # Defaulting
                transport_type='Cab' # Defaulting
            )
            pkg.save()
            print("Created Package: ID {}".format(pkg.id))
            
            # Handle Package Images
            image_ids = process_images(
                details.get('images_desktop'), 
                "Package Image", 
                user, 
                tour_operator, 
                'package', 
                pkg.id
            )
            if image_ids:
                pkg.image_ids = image_ids
                pkg.save()
                
            # 6. Parse Day-wise Itinerary
            itinerary_data = fetch_api_data("Itinerary/GetHolidayView_Itinerary/{}".format(details.get('itinerary_id')))
            if itinerary_data:
                for day_item in itinerary_data:
                    day_num = day_item.get('itinerary_day')
                    title = day_item.get('itinerary_title')
                    desc = day_item.get('itinerary_description')
                    city = day_item.get('day_destination')
                    
                    # Create DestinationPackageMapping
                    dpm = DestinationPackageMapping(
                        tour_operator_id=tour_operator,
                        package_id=pkg,
                        destination_id=destination, # Using main destination for now, or finding sub-destination?
                        day=day_num,
                        city=city,
                        title=title,
                        description=desc
                    )
                    dpm.save()
                    
                    # Process Itinerary Items (Activities/Sightseeing)
                    # The API returns 'activity' list in the day item
                    activities = day_item.get('activity', [])
                    if isinstance(activities, str):
                        try:
                            activities = json.loads(activities)
                        except:
                            activities = []
                            
                    # Wait, API analysis says 'activity' in response. sample: "activity": []
                    # If it has data, we need to adapt.
                    # Assuming generic 'sightseeing' item for the day description if no specific activities
                    
                    # Create a generic ItineraryItem for the day's description if provided
                    if desc:
                        it_item = Itineraryitem(
                            tour_operator_id=tour_operator,
                            destination=destination,
                            city=city,
                            item_type='sightseeing', # Generic
                            description=desc,
                            created_by=user
                        )
                        it_item.save()
                        
                        pkg_it_item = Packageitineraryitem(
                            package=pkg,
                            itinerary_item=it_item,
                            created_by=user,
                            day=day_num,
                            sequence=1
                        )
                        pkg_it_item.save()

            # 7. Pricing Options
            # Fetch price breakdown: /Itinerary/GetHolidayView_ItineraryPrice/{itinerary_id}/{itinerary_price_id}
            price_id = details.get('itinerary_price_id')
            if price_id:
                price_data_list = fetch_api_data("Itinerary/GetHolidayView_ItineraryPrice/{}/{}".format(details.get('itinerary_id'), price_id))
                if price_data_list:
                    price_data = price_data_list[0]
                    
                    option = PackageOption(
                        package=pkg,
                        name="Standard", # Default name as API doesn't specify option name usually
                        amount=price_data.get('traveller_total', 0),
                        description="Auto-imported option",
                        tour_operator=tour_operator,
                        created_by=user
                    )
                    option.save()
                    print("Created Package Option: {}".format(option.amount))
                    
            # 8. Inclusions/Exclusions
            # These return HTML. We'll append to package description or notes for now
            incl_resp = fetch_api_data("Itinerary/GetItinerary_InclusionsExclusions_by_ItineraryId/{}/inclusions".format(details.get('itinerary_id')))
            excl_resp = fetch_api_data("Itinerary/GetItinerary_InclusionsExclusions_by_ItineraryId/{}/exclusions".format(details.get('itinerary_id')))
            
            notes = ""
            if incl_resp:
                 notes += "<h2>Inclusions</h2>" + str(incl_resp)
            if excl_resp:
                 notes += "<h2>Exclusions</h2>" + str(excl_resp)
                
            if notes:
                pkg.notes = notes
                pkg.save()

    print("Import complete.")

if __name__ == "__main__":
    main()
