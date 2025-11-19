#!/usr/bin/env python
"""
Test script to verify the destination unique constraint works correctly.
Run this AFTER applying the migration.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Destination, Touroperator, User
from django.db import IntegrityError

def test_destination_constraint():
    """Test that the unique constraint on (tour_operator_id, name) works."""
    
    print("=" * 80)
    print("Testing Destination Unique Constraint")
    print("=" * 80)
    
    # Get or create test tour operators
    tour_op_1, _ = Touroperator.objects.get_or_create(
        email="test_op_1@example.com",
        defaults={
            'name': 'Test Tour Operator 1',
            'phone_number': '1234567890'
        }
    )
    
    tour_op_2, _ = Touroperator.objects.get_or_create(
        email="test_op_2@example.com",
        defaults={
            'name': 'Test Tour Operator 2',
            'phone_number': '0987654321'
        }
    )
    
    # Get or create a test user
    user, _ = User.objects.get_or_create(
        email="test_user@example.com",
        defaults={
            'name': 'Test User',
            'password': 'test123'
        }
    )
    
    # Clean up any existing test destinations
    Destination.objects.filter(name__startswith='TEST_DEST_').delete()
    
    print("\n✓ Test setup complete")
    
    # Test 1: Create destination for Tour Operator 1
    print("\n" + "-" * 80)
    print("Test 1: Create 'TEST_DEST_Paris' for Tour Operator 1")
    try:
        dest1 = Destination.objects.create(
            tour_operator_id=tour_op_1,
            created_by=user,
            name='TEST_DEST_Paris',
            description='Test destination'
        )
        print("✅ SUCCESS: Created destination ID:", dest1.id)
    except IntegrityError as e:
        print("❌ FAILED:", str(e))
        return
    
    # Test 2: Create same destination name for Tour Operator 2 (should succeed)
    print("\n" + "-" * 80)
    print("Test 2: Create 'TEST_DEST_Paris' for Tour Operator 2 (different operator)")
    try:
        dest2 = Destination.objects.create(
            tour_operator_id=tour_op_2,
            created_by=user,
            name='TEST_DEST_Paris',
            description='Test destination for operator 2'
        )
        print("✅ SUCCESS: Created destination ID:", dest2.id)
        print("   (Different tour operators CAN have destinations with same name)")
    except IntegrityError as e:
        print("❌ FAILED: This should have succeeded!")
        print("   Error:", str(e))
        return
    
    # Test 3: Try to create duplicate for Tour Operator 1 (should fail)
    print("\n" + "-" * 80)
    print("Test 3: Try to create duplicate 'TEST_DEST_Paris' for Tour Operator 1")
    try:
        dest3 = Destination.objects.create(
            tour_operator_id=tour_op_1,
            created_by=user,
            name='TEST_DEST_Paris',
            description='Duplicate destination'
        )
        print("❌ FAILED: This should have raised an IntegrityError!")
        print("   Created destination ID:", dest3.id)
        return
    except IntegrityError as e:
        print("✅ SUCCESS: Correctly prevented duplicate")
        print("   Error message:", str(e))
    
    # Test 4: Create different destination for Tour Operator 1 (should succeed)
    print("\n" + "-" * 80)
    print("Test 4: Create 'TEST_DEST_London' for Tour Operator 1 (different name)")
    try:
        dest4 = Destination.objects.create(
            tour_operator_id=tour_op_1,
            created_by=user,
            name='TEST_DEST_London',
            description='Different destination'
        )
        print("✅ SUCCESS: Created destination ID:", dest4.id)
        print("   (Same tour operator CAN have destinations with different names)")
    except IntegrityError as e:
        print("❌ FAILED: This should have succeeded!")
        print("   Error:", str(e))
        return
    
    # Clean up test data
    print("\n" + "-" * 80)
    print("Cleaning up test data...")
    Destination.objects.filter(name__startswith='TEST_DEST_').delete()
    print("✓ Test data cleaned up")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nThe unique constraint on (tour_operator_id, name) is working correctly:")
    print("  ✓ Different tour operators can have destinations with the same name")
    print("  ✓ Same tour operator cannot have duplicate destination names")
    print("  ✓ Same tour operator can have destinations with different names")
    print()

if __name__ == '__main__':
    test_destination_constraint()

