#!/usr/bin/env python
"""
Check if Kerala destination already exists for tour operator 1
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Destination, Touroperator

print("=" * 80)
print("Checking for existing 'Kerala' destination")
print("=" * 80)

# Check tour operator 1
tour_op_1 = Touroperator.objects.filter(id=1).first()
if not tour_op_1:
    print("❌ Tour Operator 1 not found!")
else:
    print(f"\n✅ Tour Operator 1 found: {tour_op_1.name}")
    
    # Check for Kerala destination
    kerala_dest = Destination.objects.filter(tour_operator_id=tour_op_1, name="Kerala")
    
    if kerala_dest.exists():
        print(f"\n⚠️  'Kerala' destination ALREADY EXISTS for Tour Operator 1!")
        print(f"   Count: {kerala_dest.count()}")
        print("\n   Existing records:")
        for dest in kerala_dest:
            print(f"   - ID: {dest.id}")
            print(f"     Name: {dest.name}")
            print(f"     Description: {dest.description[:100] if dest.description else 'None'}...")
            print(f"     Created by: {dest.created_by.name if dest.created_by else 'Unknown'}")
            print(f"     Created at: {dest.created_at}")
            print()
    else:
        print(f"\n✅ No 'Kerala' destination found for Tour Operator 1")
        print("   You should be able to create it.")

# Show all destinations for tour operator 1
print("\n" + "=" * 80)
print("All destinations for Tour Operator 1:")
print("=" * 80)
all_dests = Destination.objects.filter(tour_operator_id=tour_op_1)
if all_dests.exists():
    for dest in all_dests:
        print(f"- ID: {dest.id}, Name: {dest.name}, Created: {dest.created_at}")
else:
    print("No destinations found.")

