#!/usr/bin/env python
"""
Script to check for duplicate destinations before applying the unique constraint migration.
This will identify any destinations with the same name under the same tour operator.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Destination
from django.db.models import Count

# Find duplicates
duplicates = (
    Destination.objects
    .values('tour_operator_id', 'name')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

if duplicates.exists():
    print("⚠️  WARNING: Found duplicate destinations that will prevent the migration:")
    print("=" * 80)
    for dup in duplicates:
        tour_op_id = dup['tour_operator_id']
        name = dup['name']
        count = dup['count']
        
        print(f"\nTour Operator ID: {tour_op_id}")
        print(f"Destination Name: {name}")
        print(f"Duplicate Count: {count}")
        
        # Show the actual duplicate records
        dests = Destination.objects.filter(
            tour_operator_id=tour_op_id,
            name=name
        )
        print("Duplicate IDs:")
        for dest in dests:
            print(f"  - ID: {dest.id}, Created: {dest.created_at}, Created By: {dest.created_by}")
    
    print("\n" + "=" * 80)
    print("❌ You need to resolve these duplicates before running the migration.")
    print("   Options:")
    print("   1. Delete duplicate entries manually")
    print("   2. Rename duplicate entries to make them unique")
    print("   3. Merge duplicate entries if they represent the same destination")
else:
    print("✅ No duplicate destinations found!")
    print("   The migration can be applied safely.")

