#!/usr/bin/env python
"""
Delete the existing Kerala destination for tour operator 1
USE WITH CAUTION - This will permanently delete the destination!
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Destination, Touroperator

print("=" * 80)
print("⚠️  WARNING: This will DELETE the existing Kerala destination!")
print("=" * 80)

tour_op_1 = Touroperator.objects.get(id=1)
kerala_dest = Destination.objects.filter(tour_operator_id=tour_op_1, name="Kerala")

if kerala_dest.exists():
    print(f"\nFound {kerala_dest.count()} Kerala destination(s):")
    for dest in kerala_dest:
        print(f"- ID: {dest.id}, Created: {dest.created_at}")
    
    # Uncomment the line below to actually delete
    # kerala_dest.delete()
    # print("\n✅ Deleted!")
    
    print("\n⚠️  To actually delete, uncomment the delete line in the script.")
else:
    print("\n✅ No Kerala destination found to delete.")

