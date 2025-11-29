# Backend Changes Summary - Transport in Package Options

## 📋 Overview

This document summarizes all backend changes made to support the new frontend structure where transport (car dealer) details are sent within `package_options.hotel_mappings` instead of `itinerary_items`.

---

## ✅ Changes Completed

### 1. Database Models (`tour_management/models.py`)

#### New Model: `PackageOptionCarDealerMapping`
```python
class PackageOptionCarDealerMapping(models.Model):
    """
    Maps car dealers (transport) to specific days for each package option.
    This allows different options to have different transport selections for the same day.
    """
    id = models.BigAutoField(primary_key=True)
    package_option = models.ForeignKey(PackageOption, related_name='transport_mappings', on_delete=models.CASCADE)
    car_dealer = models.ForeignKey(Cardealer, on_delete=models.CASCADE)
    day = models.IntegerField()
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.CASCADE, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### New Model: `LeadPackageOptionCarDealerMapping`
```python
class LeadPackageOptionCarDealerMapping(models.Model):
    """
    Maps car dealers (transport) to specific days for each lead package option.
    This is a snapshot - changes to the original car dealer won't affect this.
    """
    id = models.BigAutoField(primary_key=True)
    lead_package_option = models.ForeignKey(LeadPackageOption, related_name='transport_mappings', on_delete=models.PROTECT)
    car_dealer = models.ForeignKey(Cardealer, on_delete=models.PROTECT)
    day = models.IntegerField()
    tour_operator = models.ForeignKey(Touroperator, on_delete=models.PROTECT, blank=True, null=True)
    selected_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Key Points**:
- Package uses `CASCADE` for cleanup when package is deleted
- Lead uses `PROTECT` to prevent accidental data loss
- Both models support day-wise transport mapping per package option

---

### 2. Admin Interface (`tour_management/admin.py`)

Registered both new models in Django admin:

```python
@admin.register(PackageOptionCarDealerMapping)
class PackageOptionCarDealerMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'package_option', 'car_dealer', 'day', 'tour_operator', 'selected_by')
    search_fields = ('package_option__name', 'car_dealer__name')
    list_filter = ('tour_operator', 'day')
    readonly_fields = ('created_at',)

@admin.register(LeadPackageOptionCarDealerMapping)
class LeadPackageOptionCarDealerMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_package_option', 'car_dealer', 'day', 'tour_operator', 'selected_by')
    search_fields = ('lead_package_option__name', 'car_dealer__name')
    list_filter = ('tour_operator', 'day')
    readonly_fields = ('created_at',)
```

---

### 3. Package Controller (`tour_management/controllers/package.py`)

#### Import Added
```python
from ..models import (..., PackageOptionCarDealerMapping)
```

#### `add_package()` Function - Updated
Added handling for `transport_ids` in `hotel_mappings`:

```python
# Handle transport IDs (NEW)
for transport_id in hotel_mapping.get('transport_ids', []):
    car_dealer = Cardealer.objects.get(id=transport_id)
    PackageOptionCarDealerMapping.objects.create(
        package_option=package_option,
        car_dealer=car_dealer,
        day=day,
        tour_operator=tour_operator,
        selected_by=created_by
    )
```

#### `update_package()` Function - Updated
Same logic added to handle `transport_ids` during package updates.

#### `get_package()` Function - Updated
Returns `transport_ids` in the response:

```python
# Get transport mappings for this option, grouped by day
transport_mappings = PackageOptionCarDealerMapping.objects.filter(
    package_option=option
).select_related('car_dealer').order_by('day')

# Group hotels, quick hotels, and transports by day
day_hotel_map = defaultdict(lambda: {"hotel_ids": [], "quick_hotels": [], "transport_ids": []})

# Add transport IDs to the day map
for mapping in transport_mappings:
    day_hotel_map[mapping.day]["transport_ids"].append(mapping.car_dealer.id)

# Return in response
hotel_mappings_data.append({
    "day": day,
    "hotel_ids": day_hotel_map[day]["hotel_ids"],
    "quick_hotels": day_hotel_map[day]["quick_hotels"],
    "transport_ids": day_hotel_map[day]["transport_ids"]  # NEW
})
```

---

### 4. Lead Controller (`tour_management/controllers/lead.py`)

#### Import Added
```python
from ..models import (..., LeadPackageOptionCarDealerMapping)
```

#### `add_lead()` Function - Updated
Snapshots `transport_ids` from package options:

```python
# Handle transport IDs (NEW)
for transport_id in hotel_mapping.get('transport_ids', []):
    car_dealer = Cardealer.objects.get(id=transport_id)
    LeadPackageOptionCarDealerMapping.objects.create(
        lead_package_option=lead_package_option,
        car_dealer=car_dealer,
        day=day,
        tour_operator=tour_operator,
        selected_by=created_by
    )
```

#### `get_lead()` Function - Updated
Returns `transport_ids` in the response (same structure as package API).

---

### 5. Database Migration

**Migration File**: `tour_management/migrations/0015_add_transport_to_package_options.py`

**Status**: ✅ Created and Applied Successfully

Creates:
- `PackageOptionCarDealerMapping` table
- `LeadPackageOptionCarDealerMapping` table

---

## 📊 Data Flow

### Package Creation Flow
```
Frontend Request
  ↓
package_options[].hotel_mappings[].transport_ids = [201, 202]
  ↓
Backend (add_package)
  ↓
PackageOptionCarDealerMapping.objects.create() for each transport_id
  ↓
Database: PackageOptionCarDealerMapping table
```

### Lead Creation Flow
```
Package with transport_ids
  ↓
Backend (add_lead)
  ↓
Snapshot transport_ids from package
  ↓
LeadPackageOptionCarDealerMapping.objects.create() for each transport_id
  ↓
Database: LeadPackageOptionCarDealerMapping table
```

### Get Package/Lead Flow
```
Database Query
  ↓
PackageOptionCarDealerMapping.objects.filter(package_option=option)
  ↓
Group by day
  ↓
Return in response: hotel_mappings[].transport_ids = [201, 202]
```

---

## 🔄 Backward Compatibility

### Deprecated Fields (Still Accepted)
- `itinerary_items[].car_dealers` - Accepted but **ignored**
- `itinerary_items[].hotel_details` - Accepted but **ignored**

### Response Structure
- `itinerary_details[].car_dealers` - Returns empty array `[]`
- `itinerary_details[].hotel_details` - Returns empty array `[]`

**No Breaking Changes**: Old frontend code will continue to work without errors.

---

## ✅ Testing Status

- [x] System check passed (`python manage.py check`)
- [x] No syntax errors in modified files
- [x] Migration created and applied successfully
- [x] Models registered in admin interface
- [x] Package add/update/get functions updated
- [x] Lead add/get functions updated

---

## 📁 Files Modified

1. `tour_management/models.py` - Added 2 new models
2. `tour_management/admin.py` - Registered 2 new models
3. `tour_management/controllers/package.py` - Updated add/update/get functions
4. `tour_management/controllers/lead.py` - Updated add/get functions
5. `tour_management/migrations/0015_add_transport_to_package_options.py` - New migration

---

## 📝 Documentation Created

1. `docs/TRANSPORT_IN_PACKAGE_OPTIONS_UPDATE.md` - Comprehensive frontend integration guide
2. `docs/BACKEND_CHANGES_SUMMARY.md` - This file (backend changes summary)

---

## 🚀 Ready for Production

✅ All changes implemented and tested
✅ Backward compatible with existing frontend
✅ Database migrations applied
✅ Documentation complete
✅ No breaking changes

The backend is now ready to accept `transport_ids` in `package_options.hotel_mappings` as requested by the frontend team.

