
import os
import django
import json
import sys

# Setup Django environment
sys.path.append('/home/sohel/code/tour_management/tour-management-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from django.test import Client

def verify_endpoints():
    client = Client()
    # Using the valid UUID we fetched from the DB
    tour_operator_id = '05a80b9d-f592-49fe-9990-7e5f811bbb46' 
    
    endpoints = [
        f'/dashboard/sales/?tour_operator_id={tour_operator_id}',
        f'/dashboard/bookings/?tour_operator_id={tour_operator_id}',
        f'/dashboard/leads/?tour_operator_id={tour_operator_id}',
        f'/dashboard/products/?tour_operator_id={tour_operator_id}',
        f'/dashboard/performance/?tour_operator_id={tour_operator_id}'
    ]

    print(f"Verifying endpoints for Tour Operator ID: {tour_operator_id}\n")

    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"SUCCESS (200 OK)")
                data = json.loads(response.content)
                print(f"Data keys: {list(data.get('data', {}).keys())}")
            else:
                print(f"FAILED ({response.status_code})")
                print(response.content)
        except Exception as e:
            print(f"EXCEPTION: {e}")
        print("-" * 40)

if __name__ == '__main__':
    verify_endpoints()
