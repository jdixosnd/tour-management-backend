
import os
import django
import sys

sys.path.append('/home/sohel/code/tour_management/tour-management-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from tour_management.models import User

print(f"{'Name':<20} | {'Role':<10} | {'UUID':<36}")
print("-" * 70)
for u in User.objects.all():
    print(f"{u.name:<20} | {str(u.role):<10} | {u.uuid}")
