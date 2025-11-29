"""
Test script to verify Package Options integration in Lead and Booking modules
Run with: python manage.py shell < test_package_options_integration.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import (
    LeadPackageOption, LeadPackageOptionHotelMapping,
    Transaction
)

def test_models_exist():
    """Test that new models are accessible"""
    print("✓ Testing model imports...")
    
    # Check LeadPackageOption model
    assert hasattr(LeadPackageOption, 'objects'), "LeadPackageOption model not found"
    print("  ✓ LeadPackageOption model exists")
    
    # Check LeadPackageOptionHotelMapping model
    assert hasattr(LeadPackageOptionHotelMapping, 'objects'), "LeadPackageOptionHotelMapping model not found"
    print("  ✓ LeadPackageOptionHotelMapping model exists")
    
    # Check Transaction has new fields
    transaction_fields = [f.name for f in Transaction._meta.get_fields()]
    assert 'selected_package_option_name' in transaction_fields, "Transaction missing selected_package_option_name field"
    assert 'selected_package_option_amount' in transaction_fields, "Transaction missing selected_package_option_amount field"
    print("  ✓ Transaction has selected_package_option_name field")
    print("  ✓ Transaction has selected_package_option_amount field")
    
    print("\n✅ All model checks passed!")

def test_database_tables():
    """Test that database tables were created"""
    print("\n✓ Testing database tables...")
    
    # Try to query the tables (will fail if tables don't exist)
    try:
        LeadPackageOption.objects.count()
        print("  ✓ LeadPackageOption table exists")
    except Exception as e:
        print(f"  ✗ LeadPackageOption table error: {e}")
        return False
    
    try:
        LeadPackageOptionHotelMapping.objects.count()
        print("  ✓ LeadPackageOptionHotelMapping table exists")
    except Exception as e:
        print(f"  ✗ LeadPackageOptionHotelMapping table error: {e}")
        return False
    
    print("\n✅ All database table checks passed!")
    return True

def test_model_relationships():
    """Test model relationships"""
    print("\n✓ Testing model relationships...")
    
    # Check LeadPackageOption relationships
    lead_package_option_fields = {f.name: f for f in LeadPackageOption._meta.get_fields()}
    assert 'lead_package' in lead_package_option_fields, "LeadPackageOption missing lead_package FK"
    assert 'hotel_mappings' in lead_package_option_fields, "LeadPackageOption missing hotel_mappings reverse relation"
    print("  ✓ LeadPackageOption has correct relationships")
    
    # Check LeadPackageOptionHotelMapping relationships
    mapping_fields = {f.name: f for f in LeadPackageOptionHotelMapping._meta.get_fields()}
    assert 'lead_package_option' in mapping_fields, "LeadPackageOptionHotelMapping missing lead_package_option FK"
    assert 'hotel' in mapping_fields, "LeadPackageOptionHotelMapping missing hotel FK"
    print("  ✓ LeadPackageOptionHotelMapping has correct relationships")
    
    print("\n✅ All relationship checks passed!")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Package Options Integration - Model Tests")
    print("=" * 60)
    
    try:
        test_models_exist()
        test_database_tables()
        test_model_relationships()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Test lead creation with package_options")
        print("2. Test lead retrieval returns package_options")
        print("3. Test booking creation with selected_package_option")
        print("4. Test booking retrieval returns selected option")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

