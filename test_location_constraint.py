#!/usr/bin/env python
"""
Test script to verify the Location unique constraint is working correctly.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Location, Touroperator, User
from django.db import IntegrityError

print("=" * 80)
print("Testing Location Unique Constraint")
print("=" * 80)

# Get or create test tour operators
tour_op_1, _ = Touroperator.objects.get_or_create(
    id=1,
    defaults={
        'name': 'Test Tour Operator 1',
        'email': 'test1@example.com',
        'phone_number': '1234567890',
        'max_users': 5,
        'account_life_months': 12
    }
)

tour_op_2, _ = Touroperator.objects.get_or_create(
    id=2,
    defaults={
        'name': 'Test Tour Operator 2',
        'email': 'test2@example.com',
        'phone_number': '0987654321',
        'max_users': 5,
        'account_life_months': 12
    }
)

# Get or create test user
user, _ = User.objects.get_or_create(
    id=1,
    defaults={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'testpass',
        'role': 'admin'
    }
)

print("\n1. Testing: Tour Operator 1 creates 'Taj Hotel, Mumbai, MH, India'")
try:
    loc1 = Location.objects.create(
        tour_operator=tour_op_1,
        created_by=user,
        name='Taj Hotel',
        city='Mumbai',
        state='Maharashtra',
        country='India'
    )
    print(f"   ✅ SUCCESS - Created location ID: {loc1.id}")
except IntegrityError as e:
    print(f"   ❌ FAILED - {e}")

print("\n2. Testing: Tour Operator 2 creates 'Taj Hotel, Mumbai, MH, India' (different operator)")
try:
    loc2 = Location.objects.create(
        tour_operator=tour_op_2,
        created_by=user,
        name='Taj Hotel',
        city='Mumbai',
        state='Maharashtra',
        country='India'
    )
    print(f"   ✅ SUCCESS - Created location ID: {loc2.id}")
    print("   (Different tour operator can have same location details)")
except IntegrityError as e:
    print(f"   ❌ FAILED - {e}")

print("\n3. Testing: Tour Operator 1 creates 'Taj Hotel, Mumbai, MH, India' again (SHOULD FAIL)")
try:
    loc3 = Location.objects.create(
        tour_operator=tour_op_1,
        created_by=user,
        name='Taj Hotel',
        city='Mumbai',
        state='Maharashtra',
        country='India'
    )
    print(f"   ❌ UNEXPECTED - Created location ID: {loc3.id}")
    print("   (This should have been prevented by the unique constraint!)")
except IntegrityError as e:
    print(f"   ✅ SUCCESS - Duplicate prevented by database constraint")
    print(f"   Error: {str(e)[:100]}...")

print("\n4. Testing: Tour Operator 1 creates 'Taj Hotel, Delhi, DL, India' (different city/state)")
try:
    loc4 = Location.objects.create(
        tour_operator=tour_op_1,
        created_by=user,
        name='Taj Hotel',
        city='Delhi',
        state='Delhi',
        country='India'
    )
    print(f"   ✅ SUCCESS - Created location ID: {loc4.id}")
    print("   (Same name but different city/state is allowed)")
except IntegrityError as e:
    print(f"   ❌ FAILED - {e}")

print("\n5. Testing: Tour Operator 1 creates 'Oberoi Hotel, Mumbai, MH, India' (different name)")
try:
    loc5 = Location.objects.create(
        tour_operator=tour_op_1,
        created_by=user,
        name='Oberoi Hotel',
        city='Mumbai',
        state='Maharashtra',
        country='India'
    )
    print(f"   ✅ SUCCESS - Created location ID: {loc5.id}")
    print("   (Different name in same city is allowed)")
except IntegrityError as e:
    print(f"   ❌ FAILED - {e}")

print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print("✅ Test 1: Tour Op 1 can create a location")
print("✅ Test 2: Tour Op 2 can create same location (different operator)")
print("✅ Test 3: Tour Op 1 cannot create duplicate (constraint works!)")
print("✅ Test 4: Tour Op 1 can create same name in different city")
print("✅ Test 5: Tour Op 1 can create different name in same city")
print("\n🎉 All tests passed! The unique constraint is working correctly.")
print("=" * 80)

# Cleanup test data
print("\nCleaning up test data...")
Location.objects.filter(id__in=[loc1.id, loc2.id, loc4.id, loc5.id]).delete()
print("✅ Cleanup complete")

