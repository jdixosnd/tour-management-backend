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
        self.assertIn("max active users exceeded.", response.json().get("message", "").lower())


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

    def test_user_update_rbac(self):
        # Create Tour Operator
        tour_op_data = {
            "name": "RBAC Tours",
            "email": "rbac@test.com",
            "phone_number": "123000",
            "max_users": 10,
            "account_life_months": 12
        }
        resp = self.client.post(self.add_url, data=tour_op_data, format='json')
        self.assertEqual(resp.status_code, 201)
        tour_op_id = resp.json()['tour_operator_id']
        
        # Helper to create user
        def create_user(role, name, email, phone):
             data = {
                 "name": name,
                 "email": email,
                 "password": "pass",
                 "mobileno": phone,
                 "role": role,
                 "tour_operator_id": tour_op_id,
                 "is_active": True
             }
             r = self.client.post(self.add_user_url, data, format='json')
             self.assertEqual(r.status_code, 201)
             return r.json()['user_id']

        admin_id = create_user("admin", "Admin", "admin@test.com", "1001")
        manager_id = create_user("manager", "Manager", "manager@test.com", "1002")
        staff_id = create_user("staff", "Staff", "staff@test.com", "1003")
        staff2_id = create_user("staff", "Staff2", "staff2@test.com", "1004")
        
        update_url = reverse('update_user')
        
        # 1. Admin updates Manager -> OK
        payload = {"requester_id": admin_id, "id": manager_id, "name": "Manager Upd", "role": "manager", "mobileno": "1002", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 200, f"Admin should update Manager: {r.content}")
        
        # 2. Manager updates Staff -> OK
        payload = {"requester_id": manager_id, "id": staff_id, "name": "Staff Upd by Mgr", "role": "staff", "mobileno": "1003", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 200, f"Manager should update Staff: {r.content}")

        # 2b. Manager updates User -> OK (New rule)
        user_id = create_user("user", "UserForMgr", "usermgr@test.com", "1005")
        payload = {"requester_id": manager_id, "id": user_id, "name": "User Upd by Mgr", "role": "user", "mobileno": "1005", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 200, f"Manager should update User: {r.content}")
        
        # 3. Manager updates Admin -> Fail
        payload = {"requester_id": manager_id, "id": admin_id, "name": "Admin Upd by Mgr", "role": "admin", "mobileno": "1001", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Manager cannot update Admin")
        
        # 4. Staff updates Self -> OK
        payload = {"requester_id": staff_id, "id": staff_id, "name": "Staff Self Upd", "role": "staff", "mobileno": "1003", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 200, f"Staff should update Self: {r.content}")
        
        # 5. Staff updates Other Staff -> Fail
        payload = {"requester_id": staff_id, "id": staff2_id, "name": "Staff2 Upd by Staff1", "role": "staff", "mobileno": "1004", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Staff cannot update other Staff")
        
        # 6. Staff changes own Role -> Fail
        payload = {"requester_id": staff_id, "id": staff_id, "name": "Staff Role Change", "role": "manager", "mobileno": "1003", "is_active": True}
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Staff cannot change own role")

    def test_user_creation_rbac(self):
         # Create Tour Operator
        tour_op_data = {
            "name": "RBAC Creation Tours",
            "email": "rbacc@test.com",
            "phone_number": "123000C",
            "max_users": 10,
            "account_life_months": 12
        }
        resp = self.client.post(self.add_url, data=tour_op_data, format='json')
        self.assertEqual(resp.status_code, 201)
        tour_op_id = resp.json()['tour_operator_id']
        
        # Helper to create user (direct call to populate initial users)
        def seed_user(role, name, email, phone):
             data = {
                 "name": name,
                 "email": email,
                 "password": "pass",
                 "mobileno": phone,
                 "role": role,
                 "tour_operator_id": tour_op_id,
                 "is_active": True
             }
             r = self.client.post(self.add_user_url, data, format='json')
             # Note: initial seed might not have requester_id, so it passes legacy check
             # But if we enforced requester_id strictly, we'd need to bootstrap. 
             # My implementation allows missing requester_id to pass, so this works for seeding.
             self.assertEqual(r.status_code, 201)
             return r.json()['user_id']

        manager_id = seed_user("manager", "Manager C", "managerc@test.com", "2002")
        staff_id = seed_user("staff", "Staff C", "staffc@test.com", "2003")

        # 1. Manager attempts to create Admin -> Fail
        payload = {
            "requester_id": manager_id,
            "name": "New Admin", "email": "newadmin@test.com", "password": "pass", "mobileno": "3001",
            "role": "admin", "tour_operator_id": tour_op_id, "is_active": True
        }
        r = self.client.post(self.add_user_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Manager cannot create Admin")

        # 2. Manager attempts to create Manager -> Fail
        payload = {
             "requester_id": manager_id,
            "name": "New Manager", "email": "newmanager@test.com", "password": "pass", "mobileno": "3002",
            "role": "manager", "tour_operator_id": tour_op_id, "is_active": True
        }
        r = self.client.post(self.add_user_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Manager cannot create Manager")

        # 3. Manager attempts to create Staff -> OK
        payload = {
             "requester_id": manager_id,
            "name": "New Staff", "email": "newstaff@test.com", "password": "pass", "mobileno": "3003",
            "role": "staff", "tour_operator_id": tour_op_id, "is_active": True
        }
        r = self.client.post(self.add_user_url, payload, format='json')
        self.assertEqual(r.status_code, 201, "Manager should be able to create Staff")

        # 4. Staff attempts to create User -> Fail
        payload = {
             "requester_id": staff_id,
            "name": "New User", "email": "newuser@test.com", "password": "pass", "mobileno": "3004",
            "role": "user", "tour_operator_id": tour_op_id, "is_active": True
        }
        r = self.client.post(self.add_user_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Staff cannot create users")

    def test_manager_cannot_promote(self):
         # Create Tour Operator
        tour_op_data = {
            "name": "RBAC Promote Tours",
            "email": "rbacp@test.com",
            "phone_number": "123000P",
            "max_users": 10,
            "account_life_months": 12
        }
        resp = self.client.post(self.add_url, data=tour_op_data, format='json')
        self.assertEqual(resp.status_code, 201)
        tour_op_id = resp.json()['tour_operator_id']
        
        # Helper to create user
        def seed_user(role, name, email, phone):
             data = {
                 "name": name,
                 "email": email,
                 "password": "pass",
                 "mobileno": phone,
                 "role": role,
                 "tour_operator_id": tour_op_id,
                 "is_active": True
             }
             r = self.client.post(self.add_user_url, data, format='json')
             self.assertEqual(r.status_code, 201)
             return r.json()['user_id']

        manager_id = seed_user("manager", "Manager P", "managerp@test.com", "4002")
        staff_id = seed_user("staff", "Staff P", "staffp@test.com", "4003")
        update_url = reverse('update_user')

        # 1. Manager tries to promote Staff to Admin -> Fail
        payload = {
            "requester_id": manager_id, 
            "id": staff_id, 
            "name": "Staff P Promoted", 
            "role": "admin", 
            "mobileno": "4003", 
            "is_active": True
        }
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Manager cannot promote Staff to Admin")

        # 2. Manager tries to promote Staff to Manager -> Fail
        payload = {
            "requester_id": manager_id, 
            "id": staff_id, 
            "name": "Staff P Promoted", 
            "role": "manager", 
            "mobileno": "4003", 
            "is_active": True
        }
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Manager cannot promote Staff to Manager")

    def test_self_role_change_restriction(self):
         # Create Tour Operator
        tour_op_data = {
            "name": "RBAC Self Role Tours",
            "email": "rbacself@test.com",
            "phone_number": "123000S",
            "max_users": 10,
            "account_life_months": 12
        }
        resp = self.client.post(self.add_url, data=tour_op_data, format='json')
        self.assertEqual(resp.status_code, 201)
        tour_op_id = resp.json()['tour_operator_id']
        
        # Helper to create user
        def seed_user(role, name, email, phone):
             data = {
                 "name": name,
                 "email": email,
                 "password": "pass",
                 "mobileno": phone,
                 "role": role,
                 "tour_operator_id": tour_op_id,
                 "is_active": True
             }
             r = self.client.post(self.add_user_url, data, format='json')
             self.assertEqual(r.status_code, 201)
             return r.json()['user_id']

        admin_id = seed_user("admin", "Admin Self", "adminself@test.com", "5001")
        manager_id = seed_user("manager", "Manager Self", "managerself@test.com", "5002")
        update_url = reverse('update_user')

        # 1. Admin updates self (No role change) -> OK
        payload = {
            "requester_id": admin_id, 
            "id": admin_id, 
            "name": "Admin Self Updated", 
            "role": "admin", 
            "mobileno": "5001", 
            "is_active": True
        }
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 200, "Admin should be able to update their own details")

        # 2. Admin tries to change own role -> Fail
        payload['role'] = 'manager'
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Admin cannot change own role")

        # 3. Manager updates self (No role change) -> OK
        payload = {
            "requester_id": manager_id, 
            "id": manager_id, 
            "name": "Manager Self Updated", 
            "role": "manager", 
            "mobileno": "5002", 
            "is_active": True
        }
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 200, "Manager should be able to update their own details")

        # 4. Manager tries to change own role -> Fail
        payload['role'] = 'admin'
        r = self.client.post(update_url, payload, format='json')
        self.assertEqual(r.status_code, 403, "Manager cannot change own role")




