# Transportation Module Removal - Frontend Integration Guide

## 📋 Overview

The backend has been updated to **remove dependencies on the transportation module**. Transportation is now handled as a simple text field (`vehicle_type`) within package options instead of managing complex car dealer objects and mappings.

### What Changed?
- ❌ **Removed**: Complex transportation object management (car dealers, car types, transport mappings)
- ✅ **Added**: Simple `vehicle_type` text field in package options
- 🎯 **Impact**: Packages, Leads, and Transactions (Bookings)

---

## 🔄 Migration Summary

### Before (Old Structure)
```json
{
  "package_options": [
    {
      "name": "Standard",
      "amount": 50000,
      "description": "Budget option",
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101, 102],
          "transport_ids": [201, 202]  // ❌ REMOVED
        }
      ]
    }
  ]
}
```

### After (New Structure)
```json
{
  "package_options": [
    {
      "name": "Standard",
      "amount": 50000,
      "description": "Budget option",
      "vehicle_type": "AC Sedan / Tempo Traveller",  // ✅ NEW
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101, 102]
        }
      ]
    }
  ]
}
```

---

## 📦 Package APIs

### 1. Create Package (`POST /package/add/`)

#### New Request Structure
```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Kerala Delight",
  "destination_id": 5,
  "no_of_days": 3,
  "package_amount": 50000,
  "description": "Beautiful Kerala tour",
  
  "itinerary_items": [
    {
      "day": 1,
      "city": "Cochin",
      "title": "Arrival in Cochin",
      "description": "Arrive and check-in",
      "hotel_details": [],  // Can be empty
      "car_dealers": []     // Can be empty
    }
  ],
  
  "package_options": [
    {
      "name": "Standard",
      "amount": 45000,
      "description": "Budget-friendly option",
      "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101, 102]
        },
        {
          "day": 2,
          "hotel_ids": [103]
        }
      ]
    },
    {
      "name": "Deluxe",
      "amount": 65000,
      "description": "Premium option",
      "vehicle_type": "AC SUV / Innova Crysta",  // ✅ NEW FIELD
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [104, 105]
        },
        {
          "day": 2,
          "hotel_ids": [106]
        }
      ]
    }
  ]
}
```

#### Response Structure
```json
{
  "message": "Package created successfully",
  "package_id": 42
}
```

---

### 2. Get Package (`POST /package/get/`)

#### Request
```json
{
  "tour_operator_id": 1,
  "package_id": 42
}
```

#### Response
```json
{
  "id": 42,
  "name": "Kerala Delight",
  "destination_id": 5,
  "no_of_days": 3,
  "package_amount": 50000.00,
  "description": "Beautiful Kerala tour",
  
  "package_options": [
    {
      "id": 100,
      "name": "Standard",
      "amount": 45000.00,
      "description": "Budget-friendly option",
      "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101, 102],
          "quick_hotels": []
        }
      ]
    },
    {
      "id": 101,
      "name": "Deluxe",
      "amount": 65000.00,
      "description": "Premium option",
      "vehicle_type": "AC SUV / Innova Crysta",  // ✅ NEW FIELD
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [104, 105],
          "quick_hotels": []
        }
      ]
    }
  ],

  "itinerary_details": [...],
  "inclusions": [...],
  "exclusions": [...],
  "images": [...]
}
```

---

### 3. Update Package (`POST /package/update/`)

Same structure as create package, but include `package_id` in the request.

---

## 📝 Lead APIs

### 1. Create Lead (`POST /lead/add/`)

#### Request Structure
```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "customer_id": 5,
  "status": "New",

  "package_snapshot": {
    "name": "Kerala Delight",
    "destination_id": 5,
    "no_of_days": 3,
    "package_amount": 50000,

    "package_options": [
      {
        "name": "Standard",
        "amount": 45000,
        "description": "Budget option",
        "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [101, 102]
          }
        ]
      },
      {
        "name": "Premium",
        "amount": 75000,
        "description": "Luxury option",
        "vehicle_type": "Mercedes / BMW",  // ✅ NEW FIELD
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [105, 106]
          }
        ]
      }
    ],

    "itinerary_details": [...],
    "inclusions": [...],
    "exclusions": [...]
  }
}
```

#### Response
```json
{
  "message": "Lead created successfully",
  "lead_id": 10,
  "lead_package_id": 15
}
```

---

### 2. Get Lead (`POST /lead/get/`)

#### Request
```json
{
  "tour_operator_id": 1,
  "lead_id": 10
}
```

#### Response
```json
{
  "id": 10,
  "customer": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210"
  },
  "status": "New",
  "created_at": "2024-01-15T10:30:00Z",

  "lead_packages": [
    {
      "id": 15,
      "name": "Kerala Delight",
      "destination_id": 5,
      "no_of_days": 3,
      "package_amount": 50000.00,

      "package_options": [
        {
          "id": 20,
          "name": "Standard",
          "amount": 45000.00,
          "description": "Budget option",
          "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
          "hotel_mappings": [...]
        },
        {
          "id": 21,
          "name": "Premium",
          "amount": 75000.00,
          "description": "Luxury option",
          "vehicle_type": "Mercedes / BMW",  // ✅ NEW FIELD
          "hotel_mappings": [...]
        }
      ],

      "itinerary_details": [...],
      "inclusions": [...],
      "exclusions": [...]
    }
  ]
}
```

---

## 🎫 Booking (Transaction) APIs

### 1. Create Booking (`POST /booking/add/`)

#### Request Structure
```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "lead_id": 10,

  "selected_package_option_name": "Standard",
  "travel_start_date": "2024-03-01",
  "travel_end_date": "2024-03-03",

  "base_amount": 45000,
  "discount_amount": 2000,
  "taxes": 2250,
  "final_amount": 45250,

  "itinerary_items": [
    {
      "day": 1,
      "title": "Arrival in Cochin",
      "description": "Check-in and relax",
      "selected_hotel_id": 101,
      "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
      "activities": [...]
    },
    {
      "day": 2,
      "title": "Cochin Sightseeing",
      "description": "Visit Fort Kochi",
      "selected_hotel_id": 101,
      "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
      "activities": [...]
    }
  ]
}
```

#### Response
```json
{
  "message": "Booking created successfully",
  "transaction_id": 50,
  "booking_id": 50
}
```

---

### 2. Get Booking (`POST /booking/get/`)

#### Request
```json
{
  "tour_operator_id": 1,
  "transaction_id": 50
}
```

#### Response
```json
{
  "id": 50,
  "customer": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "booking_status": "confirmed",
  "payment_status": "partial",
  "travel_start_date": "2024-03-01",
  "travel_end_date": "2024-03-03",

  "selected_package_option_name": "Standard",
  "base_amount": 45000.00,
  "discount_amount": 2000.00,
  "final_amount": 45250.00,

  "itinerary": [
    {
      "day": 1,
      "title": "Arrival in Cochin",
      "description": "Check-in and relax",
      "hotel": {
        "id": 101,
        "name": "Hotel Grand",
        "description": "Luxury hotel"
      },
      "vehicle_type": "AC Sedan",  // ✅ NEW FIELD
      "activities": [...]
    }
  ]
}
```

---

## 🎨 Frontend Implementation Guide

### 1. Package Creation Form

**Old Approach** (Remove this):
```javascript
// ❌ OLD - Don't use this anymore
const transportSelection = {
  day: 1,
  transport_ids: [201, 202]  // Car dealer IDs
};
```

**New Approach** (Use this):
```javascript
// ✅ NEW - Use simple text input
const packageOption = {
  name: "Standard",
  amount: 45000,
  description: "Budget option",
  vehicle_type: "AC Sedan / Tempo Traveller",  // Simple text field
  hotel_mappings: [
    {
      day: 1,
      hotel_ids: [101, 102]
    }
  ]
};
```

### 2. UI Components

#### Package Option Form
```jsx
<div className="package-option-form">
  <input
    type="text"
    name="name"
    placeholder="Option Name (e.g., Standard, Deluxe)"
    required
  />

  <input
    type="number"
    name="amount"
    placeholder="Amount"
    required
  />

  <textarea
    name="description"
    placeholder="Description (optional)"
  />

  {/* ✅ NEW FIELD */}
  <input
    type="text"
    name="vehicle_type"
    placeholder="Vehicle Type (e.g., AC Sedan, SUV, Tempo Traveller)"
  />

  {/* Hotel mappings for each day */}
  <div className="hotel-mappings">
    {/* Hotel selection UI */}
  </div>
</div>
```

#### Lead Creation
```javascript
const createLead = async (customerData, packageData) => {
  const leadData = {
    tour_operator_id: 1,
    created_by: userId,
    customer_id: customerData.id,
    status: "New",
    package_snapshot: {
      ...packageData,
      package_options: packageData.package_options.map(option => ({
        name: option.name,
        amount: option.amount,
        description: option.description,
        vehicle_type: option.vehicle_type,  // ✅ Include vehicle_type
        hotel_mappings: option.hotel_mappings
      }))
    }
  };

  const response = await fetch('/lead/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(leadData)
  });

  return await response.json();
};
```

#### Booking Creation
```javascript
const createBooking = async (leadId, selectedOption, itinerarySelections) => {
  const bookingData = {
    tour_operator_id: 1,
    created_by: userId,
    lead_id: leadId,
    selected_package_option_name: selectedOption.name,
    travel_start_date: "2024-03-01",
    travel_end_date: "2024-03-03",
    base_amount: selectedOption.amount,
    final_amount: calculateFinalAmount(),
    itinerary_items: itinerarySelections.map(item => ({
      day: item.day,
      title: item.title,
      description: item.description,
      selected_hotel_id: item.selectedHotelId,
      vehicle_type: selectedOption.vehicle_type,  // ✅ Use from selected option
      activities: item.activities
    }))
  };

  const response = await fetch('/booking/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookingData)
  });

  return await response.json();
};
```

---

## ✅ Migration Checklist

### For Frontend Developers

- [ ] **Remove** all car dealer/transport selection dropdowns from package creation forms
- [ ] **Add** simple text input field for `vehicle_type` in package options
- [ ] **Update** package creation API calls to include `vehicle_type` instead of `transport_ids`
- [ ] **Update** lead creation to pass `vehicle_type` in package snapshot
- [ ] **Update** booking creation to use `vehicle_type` instead of `selected_car_dealer_id`
- [ ] **Remove** any UI components for managing car dealers (add/edit/delete car dealers)
- [ ] **Update** display components to show `vehicle_type` as text instead of car dealer objects
- [ ] **Test** all package, lead, and booking flows with the new structure

---

## 📊 Field Mapping Reference

| Old Field | New Field | Location | Type |
|-----------|-----------|----------|------|
| `transport_ids` (array) | `vehicle_type` (string) | `package_options` | Text field |
| `selected_car_dealer_id` (int) | `vehicle_type` (string) | `itinerary_items` (booking) | Text field |
| Car dealer dropdown | Text input | Package option form | Input element |

---

## 🔍 Example Values for `vehicle_type`

Here are some example values users might enter:

- `"AC Sedan"`
- `"Non-AC Sedan"`
- `"AC SUV / Innova Crysta"`
- `"Tempo Traveller (12-seater)"`
- `"Luxury Coach"`
- `"Mercedes / BMW"`
- `"Sedan + SUV (mixed)"`
- `"As per group size"`

**Note**: This is a free-text field, so users can enter any description that makes sense for their package.

---

## 🆘 Support & Questions

If you have any questions or need clarification on the changes:

1. Check this document first
2. Review the API examples above
3. Test with the provided sample payloads
4. Contact the backend team for technical support

---

## 📅 Timeline

- **Migration Created**: Current date
- **Backward Compatibility**: Old car dealer fields are kept in the database but deprecated
- **Recommended Action**: Update frontend to use new `vehicle_type` field immediately

---

**Last Updated**: 2024-01-15
**Version**: 1.0
**Migration**: `0016_add_vehicle_type_field.py`
