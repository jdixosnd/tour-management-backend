#!/usr/bin/env python
"""
Script to check for duplicate locations before applying the unique constraint migration.
This will identify any locations with the same (tour_operator, name, city, state, country) combination.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Location
from django.db.models import Count

# Find duplicates
duplicates = (
    Location.objects
    .values('tour_operator', 'name', 'city', 'state', 'country')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

if duplicates.exists():
    print("⚠️  WARNING: Found duplicate locations that will prevent the migration:")
    print("=" * 100)
    for dup in duplicates:
        tour_op_id = dup['tour_operator']
        name = dup['name']
        city = dup['city']
        state = dup['state']
        country = dup['country']
        count = dup['count']
        
        print(f"\nTour Operator ID: {tour_op_id}")
        print(f"Location Name: {name}")
        print(f"City: {city}, State: {state}, Country: {country}")
        print(f"Duplicate Count: {count}")
        
        # Show the actual duplicate records
        locs = Location.objects.filter(
            tour_operator=tour_op_id,
            name=name,
            city=city,
            state=state,
            country=country
        )
        print("Duplicate IDs:")
        for loc in locs:
            print(f"  - ID: {loc.id}, Address: {loc.address}, Created: {loc.created_at}")
    
    print("\n" + "=" * 100)
    print("❌ You need to resolve these duplicates before running the migration.")
    print("   Options:")
    print("   1. Delete duplicate entries manually")
    print("   2. Update duplicate entries to make them unique (change name/address)")
    print("   3. Merge duplicate entries if they represent the same location")
else:
    print("✅ No duplicate locations found!")
    print("   The migration can be applied safely.")
    print("\n📊 Location Statistics:")
    total = Location.objects.count()
    by_operator = Location.objects.values('tour_operator').annotate(count=Count('id'))
    print(f"   Total locations: {total}")
    for op in by_operator:
        print(f"   Tour Operator {op['tour_operator']}: {op['count']} locations")

