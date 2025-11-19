# Location Unique Constraint Fix

## Problem Statement

The `Location` model had the **same issue** as the `Destination` model - it lacked a database-level unique constraint to prevent duplicate locations within a tour operator's namespace. This was discovered when analyzing how locations are created alongside destinations.

### Issues with Previous Implementation

1. **No Database-Level Constraint**: The model had a **commented-out** `unique_together` constraint (line 182 in models.py)
2. **Race Condition Risk**: Two simultaneous requests could create duplicate locations for the same tour operator
3. **Data Integrity**: Locations created through different code paths could bypass application-level validation
4. **Inconsistent Behavior**: Application-level checks didn't match database enforcement

### What Was Working

- ✅ Different tour operators could add their own locations
- ✅ Application-level validation in `add_location_to_db` (line 28 in location.py) prevented duplicates
- ✅ Each location had a unique `id`

### What Was Missing

- ❌ Database-level enforcement of uniqueness per tour operator
- ❌ Protection against race conditions
- ❌ Guarantee that each tour operator can only have ONE location with a given combination of (name, city, state, country)

## Solution

Enabled the **composite unique constraint** on `(tour_operator, name, city, state, country)` for the `Location` model.

### MySQL Key Length Challenge

When initially attempting to use Django's `unique_together`, we encountered:
```
django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 3072 bytes')
```

**Why this happened:**
- MySQL has a maximum index key length of **3072 bytes**
- With utf8mb4 encoding (4 bytes per character), VARCHAR(255) fields can use up to **1020 bytes** each
- Our constraint had 5 fields: `tour_operator_id` (8 bytes) + 4 VARCHAR(255) fields (4080 bytes) = **4088 bytes total**
- This exceeded the 3072-byte limit

**Solution:**
Instead of using Django's `unique_together`, we created a **custom unique index with prefix lengths** using raw SQL in the migration. This allows us to index only the first N characters of each VARCHAR field, reducing the total key size while still maintaining uniqueness for practical purposes.

### Changes Made

#### 1. Model Update (`tour_management/models.py`)

**Before (Line 180-182):**
```python
class Meta:
    db_table = 'Location'
    #unique_together = (('tour_operator', 'name','city', 'country'),)
```

**After:**
```python
class Meta:
    db_table = 'Location'
    # Note: Unique constraint is enforced via custom index in migration 0011
    # to avoid MySQL key length limit (using prefix lengths on varchar fields)
```

**Note:** We use a custom index instead of `unique_together` because:
- The combined length of all fields exceeds MySQL's 3072-byte key length limit
- With utf8mb4 encoding, VARCHAR(255) fields can use up to 1020 bytes each
- The custom index uses prefix lengths to stay within the limit
- Added `state` to the constraint because:
  - The application-level validation checks `state` (line 28 in location.py)
  - Most `get_or_create` calls include `state` in the lookup
  - Two locations can have the same name and city in different states (e.g., "Springfield, IL" vs "Springfield, MA")

#### 2. Migration Created

- **File**: `tour_management/migrations/0011_add_location_unique_constraint.py`
- **Operation**: Custom `RunSQL` to create unique index with prefix lengths
- **Index Name**: `Location_tour_operator_id_name_city_state_country_uniq`
- **Index Definition**:
  ```sql
  CREATE UNIQUE INDEX Location_tour_operator_id_name_city_state_country_uniq
  ON Location (tour_operator_id, name(100), city(100), state(50), country(50))
  ```
- **Prefix Lengths Used**:
  - `name(100)` - First 100 characters (400 bytes in utf8mb4)
  - `city(100)` - First 100 characters (400 bytes in utf8mb4)
  - `state(50)` - First 50 characters (200 bytes in utf8mb4)
  - `country(50)` - First 50 characters (200 bytes in utf8mb4)
  - `tour_operator_id` - Full field (8 bytes)
  - **Total**: ~1208 bytes (well under MySQL's 3072-byte limit)

## What This Achieves

### ✅ Correct Behavior

1. **Tour Operator Isolation**: Each tour operator can have their own "Taj Mahal Hotel, Agra, UP, India"
2. **No Duplicates Within Tour Operator**: Tour Operator A cannot create two locations with identical (name, city, state, country)
3. **Database-Level Enforcement**: The constraint is enforced by the database, preventing race conditions
4. **Data Integrity**: Ensures consistency regardless of how locations are created

### Example Scenarios

| Scenario | Tour Operator | Location Details | Result |
|----------|---------------|------------------|--------|
| Tour Op A creates "Taj Hotel, Mumbai, MH, India" | A | Taj Hotel, Mumbai, MH, India | ✅ Success |
| Tour Op B creates "Taj Hotel, Mumbai, MH, India" | B | Taj Hotel, Mumbai, MH, India | ✅ Success (different operator) |
| Tour Op A creates "Taj Hotel, Mumbai, MH, India" again | A | Taj Hotel, Mumbai, MH, India | ❌ Error (duplicate) |
| Tour Op A creates "Taj Hotel, Delhi, DL, India" | A | Taj Hotel, Delhi, DL, India | ✅ Success (different city) |
| Tour Op A creates "Taj Hotel, Mumbai, MH, India" with different address | A | Taj Hotel, Mumbai, MH, India | ❌ Error (same name/city/state/country) |

## Migration Instructions

### 1. Check for Duplicates (Already Done)

```bash
python check_duplicate_locations.py
```

**Result**: ✅ No duplicate locations found!

### 2. Apply the Migration

```bash
python manage.py migrate tour_management
```

This will add the unique constraint to the database.

### 3. Verify the Constraint

After migration, the database will enforce:
- Each `(tour_operator, name, city, state, country)` combination must be unique
- Different tour operators can have locations with the same details
- The same tour operator cannot have duplicate locations

## Impact on Existing Code

### Application-Level Validation (Already Correct)

The existing validation in `location.py` line 28 already checks the correct fields:

```python
if Location.objects.filter(
    tour_operator=touroperator,
    city=data['city'],
    state=data['state'],
    country=data['country'],
    name=data['name']
).exists():
    return {"code": 400, "error": "The location already exists."}
```

This validation will now be backed by a database constraint.

### get_or_create Calls

Multiple places use `get_or_create` with these fields:
- `destination.py` (lines 97-110)
- `hotel.py` (lines 209-222)
- `package.py` (lines 251-268)
- `lead.py` (lines 24-43)

All these calls are now protected by the database constraint.

## Benefits

1. **Data Integrity**: Database enforces business rules
2. **Race Condition Protection**: Concurrent requests cannot create duplicates
3. **Consistency**: Same behavior regardless of how data is created
4. **Multi-Tenancy Support**: Each tour operator has isolated location namespace
5. **Performance**: Database index on `(tour_operator, name, city, state, country)` improves query performance

## Why Include 'state' in the Constraint?

The original commented-out constraint was:
```python
unique_together = (('tour_operator', 'name','city', 'country'),)
```

We changed it to include `state` because:

1. **Application Logic**: The validation in `location.py` checks `state`
2. **Real-World Scenario**: Same city names exist in different states (e.g., "Springfield" exists in multiple US states)
3. **get_or_create Usage**: Most code paths include `state` in the lookup
4. **Data Accuracy**: Ensures locations are truly unique and not confused across state boundaries

## Conclusion

This fix ensures that the `Location` model properly supports multi-tenancy where each tour operator can maintain their own set of locations with unique combinations of (name, city, state, country), while preventing duplicates within each tour operator's namespace. The constraint is now enforced at both the application and database levels for maximum data integrity.

