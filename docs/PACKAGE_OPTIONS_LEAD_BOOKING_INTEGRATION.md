# Package Options Integration - Lead & Booking APIs

## 📋 Overview

Package Options have been successfully integrated into the **Lead** and **Booking (Transaction)** modules. This allows:

1. **Leads** to store multiple package options (snapshots from packages)
2. **Bookings** to track which specific option the customer selected
3. Complete data flow from Package → Lead → Booking with option tracking

---

## 🔄 Data Flow

```
Package (with multiple options)
    ↓
Lead (snapshot of all package options offered to customer)
    ↓
Booking/Transaction (customer's selected option + finalized itinerary)
```

---

## 📦 1. Lead APIs Changes

### 1.1 Add Lead API

**Endpoint:** `POST /lead/add/`

**What Changed:**
- Now accepts `package_options` array in the `package_snapshot` object
- Each option includes hotel mappings for each day

**Request Structure:**
```json
{
  "tour_operator_id": 1,
  "customer_id": 123,
  "created_by": 456,
  "package_snapshot": {
    "name": "Kerala Backwaters Tour",
    "description": "...",
    "no_of_days": 5,
    "package_amount": 25000,
    "itinerary_details": [...],
    
    "package_options": [
      {
        "name": "Standard",
        "amount": 20000,
        "description": "Budget-friendly option",
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [101, 102]
          },
          {
            "day": 2,
            "hotel_ids": [103, 104]
          }
        ]
      },
      {
        "name": "Deluxe",
        "amount": 30000,
        "description": "Premium experience",
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [201, 202]
          },
          {
            "day": 2,
            "hotel_ids": [203, 204]
          }
        ]
      }
    ]
  }
}
```

**Response:** (Same as before)
```json
{
  "message": "Lead created successfully",
  "lead_id": 789,
  "lead_package_id": 890
}
```

---

### 1.2 Get Lead API

**Endpoint:** `POST /lead/get/`

**What Changed:**
- Response now includes `package_options` array in the package object

**Request:** (No change)
```json
{
  "tour_operator_id": 1,
  "lead_id": 789
}
```

**Response Structure:**
```json
{
  "lead_id": 789,
  "customer": {...},
  "status": "active",
  "package": {
    "id": 890,
    "name": "Kerala Backwaters Tour",
    "description": "...",
    "no_of_days": 5,
    "package_amount": 25000,
    "itinerary_details": [...],
    "inclusions": [...],
    "exclusions": [...],
    "images": [...],
    
    "package_options": [
      {
        "id": 1001,
        "name": "Standard",
        "amount": 20000,
        "description": "Budget-friendly option",
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [101, 102]
          },
          {
            "day": 2,
            "hotel_ids": [103, 104]
          }
        ]
      },
      {
        "id": 1002,
        "name": "Deluxe",
        "amount": 30000,
        "description": "Premium experience",
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [201, 202]
          },
          {
            "day": 2,
            "hotel_ids": [203, 204]
          }
        ]
      }
    ]
  }
}
```

---

### 1.3 Update Lead API

**Endpoint:** `POST /lead/update/`

**What Changed:**
- Now accepts `package_options` in the `package_snapshot` object
- Deletes and recreates all package options when updating

**Request:** (Same structure as Add Lead)
**Response:** (Same as before)

---

## 🎫 2. Booking (Transaction) APIs Changes

### 2.1 Add Booking API

**Endpoint:** `POST /booking/add/`

**What Changed:**
- Now accepts `selected_package_option_name` and `selected_package_option_amount`
- These fields track which option the customer chose from the lead

**Request Structure:**
```json
{
  "tour_operator_id": 1,
  "lead_id": 789,
  "created_by": 456,
  
  "selected_package_option_name": "Deluxe",
  "selected_package_option_amount": 30000,
  
  "package_snapshot": {...},
  "itinerary_selections": [...],
  
  "base_amount": 30000,
  "discount_amount": 2000,
  "taxes": 1500,
  "final_amount": 29500,
  "amount_paid": 10000,
  "amount_due": 19500,
  
  "travel_start_date": "2024-01-15",
  "travel_end_date": "2024-01-20",
  "booking_status": "confirmed",
  "payment_status": "partial"
}
```

**Response:** (Same as before)
```json
{
  "message": "Booking created successfully",
  "transaction_id": 5001,
  "booking_id": 5001
}
```

---

### 2.2 Get Booking API

**Endpoint:** `POST /booking/get/`

**What Changed:**
- Response now includes `selected_option` object in the package section

**Request:** (No change)
```json
{
  "tour_operator_id": 1,
  "transaction_id": 5001
}
```

**Response Structure:**
```json
{
  "transaction_id": 5001,
  "booking_id": 5001,
  "lead_id": 789,

  "customer": {...},
  "tour_operator": {...},
  "destination": {...},

  "package": {
    "name": "Kerala Backwaters Tour",
    "description": "...",
    "type": "leisure",
    "pax_size": 2,
    "no_of_days": 5,

    "selected_option": {
      "name": "Deluxe",
      "amount": 30000
    },

    "inclusions": [...],
    "exclusions": [...],
    "amenities": [...],
    "policies": [...],
    "images": [...]
  },

  "itinerary": [...],

  "booking_status": "confirmed",
  "payment_status": "partial",

  "financial_details": {
    "base_amount": 30000,
    "discount_amount": 2000,
    "taxes": 1500,
    "final_amount": 29500,
    "amount_paid": 10000,
    "amount_due": 19500
  },

  "travel_start_date": "2024-01-15",
  "travel_end_date": "2024-01-20",
  "created_at": "2024-01-01T10:00:00Z"
}
```

**Note:** If no package option was selected (legacy bookings), `selected_option` will be `null`.

---

## 🗄️ 3. Database Changes

### New Tables Created:

1. **LeadPackageOption**
   - Stores package options snapshot for leads
   - Fields: `id`, `lead_package`, `name`, `amount`, `description`, `tour_operator`, `created_by`, `created_at`

2. **LeadPackageOptionHotelMapping**
   - Stores day-wise hotel selections for each lead package option
   - Fields: `id`, `lead_package_option`, `hotel`, `day`, `tour_operator`, `selected_by`, `created_at`

### Modified Tables:

**Transaction** table - Added fields:
- `selected_package_option_name` (VARCHAR 100, nullable)
- `selected_package_option_amount` (DECIMAL 15,2, nullable)

**Migration:** `0013_auto_20251125_0620.py`

---

## 💡 4. Frontend Implementation Guide

### 4.1 Creating a Lead with Package Options

When creating a lead from a package that has options:

```javascript
// Fetch package details (includes package_options)
const packageData = await fetchPackage(packageId);

// Create lead with all package options
const leadData = {
  tour_operator_id: currentOperatorId,
  customer_id: selectedCustomer.id,
  created_by: currentUser.id,
  package_snapshot: packageData  // Includes package_options array
};

const response = await createLead(leadData);
```

### 4.2 Displaying Lead Options to Customer

When showing a lead to the customer:

```javascript
// Fetch lead details
const leadData = await fetchLead(leadId);

// Display package options
leadData.package.package_options.forEach(option => {
  console.log(`${option.name}: ₹${option.amount}`);

  // Show hotels for each day
  option.hotel_mappings.forEach(mapping => {
    console.log(`Day ${mapping.day}: Hotels ${mapping.hotel_ids.join(', ')}`);
  });
});
```

### 4.3 Creating a Booking with Selected Option

When customer selects an option and confirms booking:

```javascript
// Customer selected "Deluxe" option
const selectedOption = leadData.package.package_options.find(
  opt => opt.name === "Deluxe"
);

// Create booking with selected option
const bookingData = {
  tour_operator_id: currentOperatorId,
  lead_id: leadData.lead_id,
  created_by: currentUser.id,

  // Track which option was selected
  selected_package_option_name: selectedOption.name,
  selected_package_option_amount: selectedOption.amount,

  // Financial details (based on selected option)
  base_amount: selectedOption.amount,
  discount_amount: calculatedDiscount,
  taxes: calculatedTaxes,
  final_amount: calculatedFinalAmount,

  // Customer's specific selections for each day
  itinerary_selections: [
    {
      day: 1,
      selected_hotel_id: 201,  // From Deluxe option's hotels
      selected_car_dealer_id: 301,
      activities: [...]
    },
    // ... more days
  ],

  travel_start_date: "2024-01-15",
  travel_end_date: "2024-01-20",
  booking_status: "confirmed",
  payment_status: "partial"
};

const response = await createBooking(bookingData);
```

---

## ✅ 5. Backward Compatibility

### For Packages without Options:
- `package_options` array will be empty `[]`
- `package_amount` field is still available for legacy packages
- Frontend should check: `if (package.package_options.length > 0)` to determine if options exist

### For Leads without Options:
- `package_options` array will be empty `[]`
- Lead creation/update works exactly as before if `package_options` is not provided

### For Bookings without Selected Option:
- `selected_option` will be `null` in the response
- `selected_package_option_name` and `selected_package_option_amount` are optional fields
- Legacy bookings continue to work without these fields

---

## 🧪 6. Testing Checklist

- [ ] Create a package with multiple options
- [ ] Create a lead from that package (verify options are saved)
- [ ] Retrieve the lead (verify options are returned)
- [ ] Update the lead with modified options
- [ ] Create a booking from the lead with a selected option
- [ ] Retrieve the booking (verify selected option is shown)
- [ ] Test backward compatibility with packages/leads without options
- [ ] Verify PDF generation includes selected option information

---

## 📞 7. Support

For questions or issues:
- Check existing package options documentation: `docs/package_options_api_documentation.md`
- Review frontend integration guide: `docs/FRONTEND_PACKAGE_OPTIONS_GUIDE.md`
- Contact backend team for API-related questions

---

## 🎯 Summary

**What's New:**
1. ✅ Leads now store complete package options snapshot
2. ✅ Bookings track which option customer selected
3. ✅ Full data flow: Package → Lead → Booking
4. ✅ Backward compatible with existing data
5. ✅ Database migrations applied successfully

**Frontend Action Items:**
1. Update lead creation to pass `package_options` from package snapshot
2. Display package options when showing leads to customers
3. Allow customer to select an option when creating booking
4. Pass `selected_package_option_name` and `selected_package_option_amount` when creating bookings
5. Display selected option in booking details view


