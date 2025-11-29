# Transport in Package Options - Backend Update

## 📋 Overview

The backend has been updated to support the new frontend structure where **transport (car dealer) details are now sent within `package_options.hotel_mappings`** instead of `itinerary_items`.

This document outlines the changes made and confirms backward compatibility.

---

## ✅ Changes Implemented

### 1. New Database Models

**PackageOptionCarDealerMapping**
- Maps car dealers (transport) to specific days for each package option
- Allows different package options to have different transport selections per day
- Fields: `package_option`, `car_dealer`, `day`, `tour_operator`, `selected_by`, `created_at`

**LeadPackageOptionCarDealerMapping**
- Snapshot of transport mappings in leads
- Preserves transport selections when lead is created from package
- Fields: `lead_package_option`, `car_dealer`, `day`, `tour_operator`, `selected_by`, `created_at`

**Migration**: `0015_add_transport_to_package_options.py` ✅ Applied

---

### 2. API Changes

#### Package Create/Update APIs

**Endpoints**: `POST /package/add/` and `POST /package/update/`

**New Request Structure**:

```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Kerala Delight",
  "destination_id": 5,
  "itinerary_items": [
    {
      "day": 1,
      "city": "Cochin",
      "hotel_details": [],  // ✅ DEPRECATED - Can be sent as empty array
      "car_dealers": []     // ✅ DEPRECATED - Can be sent as empty array
    }
  ],
  "package_options": [
    {
      "name": "Standard",
      "amount": 50000,
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101, 102],       // Hotels for this option/day
          "transport_ids": [201, 202],   // ✅ NEW - Transport for this option/day
          "quick_hotels": [...]          // Quick hotels (if any)
        },
        {
          "day": 2,
          "hotel_ids": [103],
          "transport_ids": [203],
          "quick_hotels": []
        }
      ]
    },
    {
      "name": "Deluxe",
      "amount": 75000,
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [104, 105],
          "transport_ids": [204],
          "quick_hotels": []
        }
      ]
    }
  ]
}
```

**Key Points**:
- ✅ `transport_ids` is now accepted in `package_options[].hotel_mappings[]`
- ✅ `itinerary_items[].car_dealers` is **deprecated** but still accepted (will be ignored)
- ✅ `itinerary_items[].hotel_details` is **deprecated** but still accepted (will be ignored)
- ✅ Backend now reads transport data **only** from `package_options.hotel_mappings`

---

#### Package Get API

**Endpoint**: `POST /package/get/`

**New Response Structure**:

```json
{
  "id": 42,
  "name": "Kerala Delight",
  "destination_id": 5,
  "package_options": [
    {
      "id": 100,
      "name": "Standard",
      "amount": 50000.00,
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101, 102],
          "transport_ids": [201, 202],   // ✅ NEW - Transport IDs returned here
          "quick_hotels": [...]
        },
        {
          "day": 2,
          "hotel_ids": [103],
          "transport_ids": [203],
          "quick_hotels": []
        }
      ]
    }
  ],
  "itinerary_details": [
    {
      "day": 1,
      "city": "Cochin",
      "hotel_details": [],  // ✅ Empty (deprecated)
      "car_dealers": []     // ✅ Empty (deprecated)
    }
  ]
}
```

**Key Points**:
- ✅ `transport_ids` is now returned in `package_options[].hotel_mappings[]`
- ✅ `itinerary_details[].car_dealers` returns empty array (deprecated)
- ✅ `itinerary_details[].hotel_details` returns empty array (deprecated)

---

#### Lead APIs

**Endpoints**: `POST /lead/add/` and `POST /lead/get/`

**Changes**:
- ✅ Lead creation now snapshots `transport_ids` from package options
- ✅ Lead retrieval returns `transport_ids` in `package_options.hotel_mappings`
- ✅ Same structure as package APIs

---

## 🔄 Backward Compatibility

### What Still Works

1. **Old Request Format** (sending `car_dealers` in `itinerary_items`):
   - ✅ Backend accepts it without errors
   - ⚠️ Data is **ignored** (not saved)
   - ✅ No breaking changes for existing frontend code

2. **Old Response Format** (reading from `itinerary_details`):
   - ✅ `itinerary_details[].car_dealers` still exists in response
   - ✅ Returns empty array `[]`
   - ⚠️ Frontend should migrate to reading from `package_options.hotel_mappings`

### Migration Path

**Phase 1** (Current):
- Frontend sends `transport_ids` in `package_options.hotel_mappings`
- Frontend can still send empty arrays in `itinerary_items.car_dealers` (will be ignored)

**Phase 2** (Future):
- Frontend stops sending `itinerary_items.car_dealers` entirely
- Backend can remove deprecated fields in future version

---

## 📊 Data Flow

### Package Creation
```
Frontend sends transport_ids in package_options.hotel_mappings
    ↓
Backend creates PackageOptionCarDealerMapping records
    ↓
Transport selections stored per package option per day
```

### Lead Creation
```
Package with transport_ids
    ↓
Lead snapshots transport_ids from package
    ↓
LeadPackageOptionCarDealerMapping records created
    ↓
Transport selections preserved in lead
```

### Booking Creation
```
Lead with transport_ids
    ↓
Customer selects one transport per day
    ↓
Booking stores selected transport
    ↓
(No changes needed in booking flow)
```

---

## 🧪 Testing Checklist

### Package Module
- [x] Create package with `transport_ids` in `package_options.hotel_mappings`
- [x] Update package with new `transport_ids`
- [x] Get package - verify `transport_ids` returned in response
- [x] Create package with empty `itinerary_items.car_dealers` (should work)

### Lead Module
- [x] Create lead from package with `transport_ids`
- [x] Get lead - verify `transport_ids` in `package_options.hotel_mappings`
- [x] Verify transport data is snapshotted correctly

---

## 📝 Code Changes Summary

### Files Modified

1. **tour_management/models.py**
   - Added `PackageOptionCarDealerMapping` model
   - Added `LeadPackageOptionCarDealerMapping` model

2. **tour_management/admin.py**
   - Registered `PackageOptionCarDealerMapping` in admin
   - Registered `LeadPackageOptionCarDealerMapping` in admin

3. **tour_management/controllers/package.py**
   - Updated `add_package()` to handle `transport_ids` in `hotel_mappings`
   - Updated `update_package()` to handle `transport_ids` in `hotel_mappings`
   - Updated `get_package()` to return `transport_ids` in response

4. **tour_management/controllers/lead.py**
   - Updated `add_lead()` to snapshot `transport_ids` from package
   - Updated `get_lead()` to return `transport_ids` in response

5. **tour_management/migrations/**
   - Created `0015_add_transport_to_package_options.py`

---

## 💡 Frontend Integration Examples

### Creating a Package

```javascript
const createPackage = async () => {
  const packageData = {
    tour_operator_id: 1,
    created_by: 1,
    name: "Kerala Delight",
    destination_id: 5,

    // Deprecated fields - can send as empty
    itinerary_items: [
      {
        day: 1,
        city: "Cochin",
        hotel_details: [],  // Empty (deprecated)
        car_dealers: []     // Empty (deprecated)
      }
    ],

    // NEW: Transport in package options
    package_options: [
      {
        name: "Standard",
        amount: 50000,
        hotel_mappings: [
          {
            day: 1,
            hotel_ids: [101, 102],
            transport_ids: [201, 202],  // ✅ Transport here
            quick_hotels: []
          }
        ]
      }
    ]
  };

  const response = await fetch('/package/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(packageData)
  });

  return await response.json();
};
```

### Displaying Package Options with Transport

```javascript
const displayPackageOptions = (packageData) => {
  packageData.package_options.forEach(option => {
    console.log(`Option: ${option.name} - ₹${option.amount}`);

    option.hotel_mappings.forEach(mapping => {
      console.log(`  Day ${mapping.day}:`);
      console.log(`    Hotels: ${mapping.hotel_ids.join(', ')}`);
      console.log(`    Transport: ${mapping.transport_ids.join(', ')}`);  // ✅ Read from here

      if (mapping.quick_hotels.length > 0) {
        console.log(`    Quick Hotels: ${mapping.quick_hotels.length}`);
      }
    });
  });
};
```

### State Management

```javascript
// Package state structure
const [packageData, setPackageData] = useState({
  name: "",
  destination_id: null,
  package_options: [
    {
      name: "Standard",
      amount: 0,
      hotel_mappings: [
        {
          day: 1,
          hotel_ids: [],
          transport_ids: [],      // ✅ Transport IDs here
          quick_hotels: []
        }
      ]
    }
  ]
});

// Add transport to a specific day
const addTransport = (optionIndex, day, transportId) => {
  setPackageData(prev => {
    const updated = { ...prev };
    const mapping = updated.package_options[optionIndex]
      .hotel_mappings.find(m => m.day === day);

    if (!mapping.transport_ids) {
      mapping.transport_ids = [];
    }

    mapping.transport_ids.push(transportId);
    return updated;
  });
};

// Remove transport from a specific day
const removeTransport = (optionIndex, day, transportId) => {
  setPackageData(prev => {
    const updated = { ...prev };
    const mapping = updated.package_options[optionIndex]
      .hotel_mappings.find(m => m.day === day);

    mapping.transport_ids = mapping.transport_ids.filter(id => id !== transportId);
    return updated;
  });
};
```

---

## ⚠️ Important Notes

1. **Deprecated Fields**:
   - `itinerary_items[].car_dealers` - No longer used for storage
   - `itinerary_items[].hotel_details` - No longer used for storage
   - These fields can be sent as empty arrays `[]`

2. **New Location**:
   - Transport IDs are now in `package_options[].hotel_mappings[].transport_ids`
   - This allows different package options to have different transport selections

3. **Multiple Transports**:
   - `transport_ids` is an array, allowing multiple transport options per day
   - Customer can select one during booking

4. **Consistency**:
   - Same structure used in both Package and Lead APIs
   - Booking API remains unchanged (customer selects from available options)

---

## 🚀 Next Steps for Frontend Team

1. ✅ Update package creation form to send `transport_ids` in `package_options.hotel_mappings`
2. ✅ Update package display to read `transport_ids` from `package_options.hotel_mappings`
3. ✅ Remove code that sends data to `itinerary_items.car_dealers` (optional, for cleanup)
4. ✅ Remove code that reads from `itinerary_details.car_dealers` (optional, for cleanup)
5. ✅ Test package creation, update, and retrieval with new structure
6. ✅ Test lead creation from packages with transport options
7. ✅ Verify booking flow still works correctly

---

## 📞 Support

For questions or issues related to this update, please contact the backend team.

**Summary**:
- ✅ Backend fully supports new structure with `transport_ids` in `package_options.hotel_mappings`
- ✅ Backward compatible - old fields still accepted (but ignored)
- ✅ All APIs updated: Package (add/update/get) and Lead (add/get)
- ✅ Database migrations applied successfully
- ✅ Ready for frontend integration

