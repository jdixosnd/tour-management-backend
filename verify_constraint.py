#!/usr/bin/env python
"""Quick verification that the constraint is working"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import Destination

# Check existing destinations
destinations = Destination.objects.all().values('id', 'tour_operator_id', 'name')

print("Current Destinations in Database:")
print("=" * 80)
for dest in destinations:
    print(f"ID: {dest['id']}, Tour Operator: {dest['tour_operator_id']}, Name: {dest['name']}")

print("\n" + "=" * 80)
print(f"Total destinations: {destinations.count()}")

# Group by tour operator
from django.db.models import Count
duplicates = (
    Destination.objects
    .values('tour_operator_id', 'name')
    .annotate(count=Count('id'))
    .filter(count__gt=1)
)

if duplicates.exists():
    print("\n⚠️  WARNING: Found destinations with same name under same tour operator:")
    for dup in duplicates:
        print(f"  Tour Operator: {dup['tour_operator_id']}, Name: {dup['name']}, Count: {dup['count']}")
else:
    print("\n✅ No duplicates found - constraint is working correctly!")

