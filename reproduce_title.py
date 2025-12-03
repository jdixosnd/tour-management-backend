import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tour_management_project.settings")
django.setup()

from tour_management.models import (
    User, Touroperator, Destination, Package, DestinationPackageMapping, Itineraryitem, Packageitineraryitem
)
from tour_management.controllers.package import add_package, get_package

def test_day_title():
    # Setup data
    try:
        operator = Touroperator.objects.first()
        if not operator:
            operator = Touroperator.objects.create(name="Test Operator", email="test@test.com")
        
        user = User.objects.first()
        if not user:
            user = User.objects.create(name="Test User", email="user@test.com", tour_operator_id=operator)
            
        destination = Destination.objects.first()
        if not destination:
            destination = Destination.objects.create(name="Test Dest", tour_operator_id=operator, created_by=user)

        # Create package payload with Day Title
        payload = {
            "tour_operator_id": operator.id,
            "created_by": user.id,
            "name": "Test Package with Title",
            "type": "family",
            "destination_id": destination.id,
            "itinerary_items": [
                {
                    "day": 1,
                    "city": "Paris",
                    "state": "IDF",
                    "title": "Arrival in Paris",  # <--- The field in question
                    "description": "Day 1 description",
                    "activities": []
                }
            ]
        }

        # Mock request
        class MockRequest:
            method = 'POST'
            body = json.dumps(payload).encode('utf-8')

        # Call add_package
        response = add_package(MockRequest())
        print(f"Add Package Response: {response.status_code} - {response.content}")
        
        if response.status_code != 201:
            return

        package_id = json.loads(response.content)['package_id']
        
        # Verify in DB
        mapping = DestinationPackageMapping.objects.get(package_id=package_id, day=1)
        print(f"DB Title: {mapping.title}")
        
        # Verify in get_package
        payload_get = {
            "tour_operator_id": operator.id,
            "package_id": package_id
        }
        class MockGetRequest:
            method = 'POST'
            body = json.dumps(payload_get).encode('utf-8')
            
        response_get = get_package(MockGetRequest())
        data = json.loads(response_get.content)['data'][0]
        day_details = data['itinerary_details'][0]
        print(f"API Title: {day_details['title']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_day_title()
