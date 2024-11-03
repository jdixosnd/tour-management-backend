from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Touroperator
import  logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class TouroperatorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.add_url = reverse('add_tour_operator') 
        self.get_url = reverse('get_tour_operators')
        self.add_user_url = reverse('add_user')
    def test_add_tour_operator(self):
        # Define the request data
        request_data = {
            "name": "Adventure Tours Ltd.",
            "email": "contact@adventuretours.com",
            "phone_number": "+1234567890",
            "address": "1234 Adventure Street, Travel City, Country",
            "max_users": 3,
            "renewal_date": "2025-12-31T00:00:00Z",
            "account_life_months": 12
        }

        # Make the POST request
        response = self.client.post(self.add_url, data=request_data, format='json')
        logger.info(f"Response Status Code: {response}")
        logger.info(f"Response JSON: {response.json()}")        # Check the response status code and content
        self.assertEqual(response.status_code, 201)

        # Verify the Touroperator was created in the database
        self.assertTrue(Touroperator.objects.filter(email="contact@adventuretours.com").exists())
    
    def test_validate_more_users_than_permitted(self):

        # Define the request data
        request_data = {
            "name": "Adventure Tours Ltd.",
            "email": "contact@adventuretours.com",
            "phone_number": "+1234567890",
            "address": "1234 Adventure Street, Travel City, Country",
            "max_users": 3,
            "renewal_date": "2025-12-31T00:00:00Z",
            "account_life_months": 12
        }

        # Make the POST request
        response = self.client.post(self.add_url, data=request_data, format='json')
        logger.info(f"Response Status Code: {response}")
        logger.info(f"Response JSON: {response.json()}")        # Check the response status code and content+
        tour_operator_id = response.json().get("tour_operator_id")

        self.assertEqual(response.status_code, 201)

        # Verify the Touroperator was created in the database
        self.assertTrue(Touroperator.objects.filter(email="contact@adventuretours.com").exists())
     

        # Retrieving the added tour operator
        response = self.client.post(self.get_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        logging.info(response.json())
     
        self.assertTrue(any(op['name'] == "Adventure Tours Ltd." for op in response.json()))



        user_data = [
            {"name": "Manager One", "email": "manager@adventuretours.com", "password": "manager123", "mobileno":"9863251256","role": "manager", "tour_operator_id": tour_operator_id, "is_active": True},
            {"name": "User One", "email": "user1@adventuretours.com", "password": "user123", "role": "user", "mobileno":"9632541258", "tour_operator_id": tour_operator_id, "is_active": True},
            {"name": "User Two", "email": "user2@adventuretours.com", "password": "user123", "role": "user", "mobileno":"9879875424", "tour_operator_id": tour_operator_id, "is_active": True},
        ]
        
        for user in user_data:
            response = self.client.post(self.add_user_url, user, format='json')
            self.assertEqual(response.status_code, 201)

        response = self.client.post(self.add_user_url, {
            "name": "User Three", "email": "user3@adventuretours.com", "password": "user123", "mobileno":"9879876424", "role": "user", "tour_operator_id": tour_operator_id, "is_active": True
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("max active users exceeded.", response.json().get("error", "").lower())


    def test_adding_getting_destination(self):

        # Define the request data
        request_data = {
            "name": "Adventure Tours Ltd.",
            "email": "contact@adventuretours.com",
            "phone_number": "+1234567890",
            "address": "1234 Adventure Street, Travel City, Country",
            "max_users": 3,
            "renewal_date": "2025-12-31T00:00:00Z",
            "account_life_months": 12
        }

        # Make the POST request
        response = self.client.post(self.add_url, data=request_data, format='json')
        logger.info(f"Response Status Code: {response}")
        logger.info(f"Response JSON: {response.json()}")        # Check the response status code and content+
        tour_operator_id = response.json().get("tour_operator_id")

        self.assertEqual(response.status_code, 201)

        # Verify the Touroperator was created in the database
        self.assertTrue(Touroperator.objects.filter(email="contact@adventuretours.com").exists())
     

        # Retrieving the added tour operator
        response = self.client.post(self.get_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        logging.info(response.json())
     
        self.assertTrue(any(op['name'] == "Adventure Tours Ltd." for op in response.json()))



        user_data = [
            {"name": "Manager One", "email": "manager@adventuretours.com", "password": "manager123", "mobileno":"9863251256","role": "manager", "tour_operator_id": tour_operator_id, "is_active": True},
            {"name": "User One", "email": "user1@adventuretours.com", "password": "user123", "role": "user", "mobileno":"9632541258", "tour_operator_id": tour_operator_id, "is_active": True},
            {"name": "User Two", "email": "user2@adventuretours.com", "password": "user123", "role": "user", "mobileno":"9879875424", "tour_operator_id": tour_operator_id, "is_active": True},
        ]
        user_id = None
        for u in user_data:
            response = self.client.post(self.add_user_url, u, format='json')
            self.assertEqual(response.status_code, 201)
            user_id = response.json()['user_id']




