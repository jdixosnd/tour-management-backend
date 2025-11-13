# Booking (Transaction) API - UI Team Guide

## 📋 Overview

In the UI, you have a **Lead** with multiple hotel and transport options. When the customer is ready to book, they click a **"Book Now"** or **"Convert to Booking"** button. This creates a **Transaction** (which we call "Booking" in the UI).

---

## 🔄 User Flow

```
Lead Screen (Multiple Options)
    ↓
Customer Reviews Options
    ↓
Customer Selects Preferences (1 hotel + 1 transport per day)
    ↓
[Book Now Button] ← You are here
    ↓
Create Transaction/Booking
    ↓
Booking Confirmation Screen
```

---

## 🎯 What You Need to Know

### 1. Lead vs Booking (Transaction)

| Aspect | Lead | Booking (Transaction) |
|--------|------|----------------------|
| **Purpose** | Proposal/Quote | Confirmed Booking |
| **Hotels per Day** | Multiple options (2-5 hotels) | ONE selected hotel |
| **Transport per Day** | Multiple options (2-3 options) | ONE selected transport |
| **Status** | "pending", "shared", "accepted", "rejected" | `booking_status` + `payment_status` |
| **Customer Action** | Review and choose | Pay and travel |

### 2. The "Book Now" Button Flow

When customer clicks **"Book Now"** on a Lead:

**Step 1: Customer Selection UI**
- Show all hotel options for each day
- Customer selects ONE hotel per day
- Show all transport options for each day
- Customer selects ONE transport per day
- Customer enters payment details

**Step 2: Create Booking**
- Call `POST /transaction/add/` with:
  - `lead_id` (the lead they're booking from)
  - `itinerary_selections` (their selected hotel/transport IDs)
  - Payment details

**Step 3: Show Confirmation**
- Display booking confirmation
- Show selected hotels and transports
- Show payment status

---

## 🚨 Important Changes from Old System

### OLD System (Deprecated)
```javascript
// ❌ OLD - Don't use anymore
POST /transaction/add/
{
  "customer_id": 1,
  "package_snapshot": {
    "itinerary_details": [
      {
        "day": 1,
        "hotel_details": {...},  // Full hotel object
        "car_dealer_details": {...}  // Full transport object
      }
    ]
  }
}
```

### NEW System (Current)
```javascript
// ✅ NEW - Use this
POST /transaction/add/
{
  "lead_id": 3,  // Required: The lead being booked
  "created_by": 1,
  "itinerary_selections": [  // Customer's choices
    {
      "day": 1,
      "selected_hotel_id": 4,  // Just the ID
      "selected_car_dealer_id": 2  // Just the ID
    }
  ],
  "base_amount": 70000.00,
  "final_amount": 68500.00,
  "booking_status": "confirmed",
  "payment_status": "partial"
}
```

### Key Differences

| What Changed | OLD | NEW |
|--------------|-----|-----|
| **Entry Point** | Direct from package | From Lead (required) |
| **Hotel/Transport** | Full object embedded | Just IDs |
| **Field Name** | `itinerary_details` | `itinerary_selections` |
| **Status** | Single `status` field | `booking_status` + `payment_status` |
| **Payment** | Only `final_amount` | `base_amount`, `discount_amount`, `taxes`, `final_amount`, `amount_paid`, `amount_due` |

---

---

## 📝 API Details

### Endpoint: Create Booking

**URL:** `POST /transaction/add/`

**When to call:** When customer clicks "Book Now" button on a Lead

### Building the Request from Lead Data

**Step 1: Get the Lead**
```javascript
// You already have the lead displayed in UI
const lead = {
  id: 3,
  customer: {...},
  package: {
    name: "Kerala Delight",
    description: "...",
    inclusions: [...],
    exclusions: [...],
    amenities: [...],
    policies: [...],
    images: [...]
  },
  itinerary_details: [
    {
      day: 1,
      title: "Arrival in Kochi",
      hotel_details: [
        {id: 4, name: "Hotel A", ...},
        {id: 5, name: "Hotel B", ...},
        {id: 6, name: "Hotel C", ...}
      ],
      car_dealer_details: [
        {id: 2, name: "Sedan", ...},
        {id: 3, name: "SUV", ...}
      ],
      activities: [...]
    },
    {
      day: 2,
      title: "Kochi Sightseeing",
      hotel_details: [...],
      car_dealer_details: [...],
      activities: [...]
    }
  ]
}
```

**Step 2: Customer Selects Options**
```javascript
// In your UI, customer selects ONE hotel and ONE transport per day
const customerSelections = {
  day1: {
    selectedHotelId: 4,  // Customer picked "Hotel A"
    selectedTransportId: 2  // Customer picked "Sedan"
  },
  day2: {
    selectedHotelId: 7,
    selectedTransportId: 3
  }
}
```

**Step 3: Build Transaction Request**
```javascript
const bookingRequest = {
  lead_id: lead.id,  // ✅ Required
  created_by: currentUserId,

  // Copy package-level data from lead
  package_snapshot: {
    name: lead.package.name,
    description: lead.package.description,
    type: lead.package.type,
    pax_size: lead.package.pax_size,
    no_of_days: lead.package.no_of_days,
    inclusions: lead.package.inclusions,
    exclusions: lead.package.exclusions,
    amenities: lead.package.amenities,
    policies: lead.package.policies,
    images: lead.package.images
  },

  // Map customer selections to itinerary_selections
  itinerary_selections: lead.itinerary_details.map(day => ({
    day: day.day,
    title: day.title,
    description: day.description,
    selected_hotel_id: customerSelections[`day${day.day}`].selectedHotelId,
    selected_car_dealer_id: customerSelections[`day${day.day}`].selectedTransportId,
    activities: day.activities
  })),

  // Financial details
  base_amount: calculatedBaseAmount,
  discount_amount: discountApplied,
  taxes: calculatedTaxes,
  final_amount: totalAmount,
  amount_paid: initialPayment,
  amount_due: totalAmount - initialPayment,

  // Booking details
  travel_start_date: "2025-12-01",
  travel_end_date: "2025-12-05",
  booking_status: "confirmed",  // or "pending"
  payment_status: initialPayment > 0 ? "partial" : "unpaid",
  booking_notes: "Customer requested early check-in"
}
```

### Complete Request Example

```json
{
  "lead_id": 3,
  "created_by": 1,
  
  "package_snapshot": {
    "name": "Kerala Delight",
    "description": "5 days Kerala tour",
    "type": "family",
    "pax_size": 4,
    "no_of_days": 5,
    "inclusions": [
      {"id": 1, "name": "Breakfast", "description": "Daily breakfast"}
    ],
    "exclusions": [
      {"id": 2, "name": "Lunch", "description": "Lunch not included"}
    ],
    "amenities": [...],
    "policies": [...],
    "images": [...]
  },
  
  "itinerary_selections": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "description": "Check-in and relax",
      "selected_hotel_id": 4,  // ✅ Customer selected THIS hotel from lead's multiple options
      "selected_car_dealer_id": 2,  // ✅ Customer selected THIS transport from lead's multiple options
      "activities": [
        {
          "type": "sightseeing",
          "name": "Fort Kochi",
          "description": "Visit historic fort",
          "images": [...]
        }
      ]
    },
    {
      "day": 2,
      "title": "Kochi to Munnar",
      "description": "Travel to Munnar",
      "selected_hotel_id": 7,  // ✅ Different hotel for day 2
      "selected_car_dealer_id": 3,  // ✅ Different transport for day 2
      "activities": [...]
    }
    // ... more days
  ],
  
  "base_amount": 70000.00,
  "discount_amount": 5000.00,
  "taxes": 3500.00,
  "final_amount": 68500.00,
  "amount_paid": 20000.00,
  "amount_due": 48500.00,
  
  "travel_start_date": "2025-12-01",
  "travel_end_date": "2025-12-05",
  
  "booking_status": "confirmed",
  "payment_status": "partial",
  "booking_notes": "Customer requested early check-in"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `lead_id` | Integer | ID of the lead (must exist) |
| `created_by` | Integer | User ID creating the transaction |
| `package_snapshot` | Object | Package-level data (name, description, inclusions, exclusions, amenities, policies, images) |
| `itinerary_selections` | Array | Day-wise customer selections |
| `base_amount` | Decimal | Base package amount |
| `final_amount` | Decimal | Final amount after discount and taxes |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `discount_amount` | Decimal | 0.0 | Discount applied |
| `taxes` | Decimal | 0.0 | Tax amount |
| `amount_paid` | Decimal | 0.0 | Amount already paid |
| `amount_due` | Decimal | final_amount | Amount remaining |
| `travel_start_date` | Date | null | Travel start date (YYYY-MM-DD) |
| `travel_end_date` | Date | null | Travel end date (YYYY-MM-DD) |
| `booking_status` | String | "pending" | "pending", "confirmed", "cancelled", "completed" |
| `payment_status` | String | "unpaid" | "unpaid", "partial", "paid", "refunded" |
| `booking_notes` | String | "" | Additional notes |

### Itinerary Selection Structure

Each item in `itinerary_selections` array:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `day` | Integer | Yes | Day number |
| `title` | String | No | Day title |
| `description` | String | No | Day description |
| `selected_hotel_id` | Integer | No | Customer's chosen hotel ID |
| `selected_car_dealer_id` | Integer | No | Customer's chosen transport ID |
| `activities` | Array | No | List of activity objects |

### Response

```json
{
  "message": "Transaction created successfully",
  "transaction_id": 15
}
```

### Error Responses

```json
// Missing required fields
{
  "error": "Missing fields: lead_id, base_amount"
}

// Lead not found
{
  "error": "Lead not found"
}

// No package in lead
{
  "error": "No package found for this lead"
}
```

---

## How to Build the Request

### Step 1: Get Lead Data
```json
POST /lead/get/
{
  "lead_id": 3
}
```

**Response includes:**
```json
{
  "lead_id": 3,
  "package": {
    "name": "Kerala Delight",
    "inclusions": [...],
    "exclusions": [...],
    ...
  },
  "itinerary_details": [
    {
      "day": 1,
      "title": "Arrival",
      "hotel_details": [  // ⚠️ MULTIPLE OPTIONS
        {"id": 4, "name": "Hotel A", ...},
        {"id": 5, "name": "Hotel B", ...},
        {"id": 6, "name": "Hotel C", ...}
      ],
      "car_dealer_details": [  // ⚠️ MULTIPLE OPTIONS
        {"id": 2, "name": "Dealer X", ...},
        {"id": 3, "name": "Dealer Y", ...}
      ],
      "activities": [...]
    }
  ]
}
```

### Step 2: Customer Selects Options

Show the customer all hotel and transport options for each day. Let them select ONE of each.

### Step 3: Build Transaction Request

```javascript
const transactionRequest = {
  lead_id: leadData.lead_id,
  created_by: userId,
  
  // Copy package-level data from lead
  package_snapshot: {
    name: leadData.package.name,
    description: leadData.package.description,
    inclusions: leadData.package.inclusions,
    exclusions: leadData.package.exclusions,
    amenities: leadData.package.amenities,
    policies: leadData.package.policies,
    images: leadData.package.images
  },
  
  // Build itinerary with customer's selections
  itinerary_selections: leadData.itinerary_details.map(day => ({
    day: day.day,
    title: day.title,
    description: day.description,
    selected_hotel_id: customerSelectedHotelId[day.day],  // ✅ Customer's choice
    selected_car_dealer_id: customerSelectedTransportId[day.day],  // ✅ Customer's choice
    activities: day.activities  // Same activities
  })),
  
  // Financial details
  base_amount: calculatedAmount,
  discount_amount: discount,
  taxes: taxes,
  final_amount: finalAmount,
  
  // ... other fields
};
```

---

## Migration Guide for UI Team

### Step 1: Update Transaction Creation Flow

**OLD CODE (Remove):**
```javascript
// ❌ OLD - Don't use this anymore
const createTransaction = async (packageData) => {
  const response = await fetch('/transaction/add/', {
    method: 'POST',
    body: JSON.stringify({
      customer_id: customerId,
      package_snapshot: packageData  // Full package with itinerary_details
    })
  });
};
```

**NEW CODE (Use this):**
```javascript
// ✅ NEW - Use this structure
const createTransaction = async (leadId, customerSelections) => {
  // First, get lead data
  const leadResponse = await fetch('/lead/get/', {
    method: 'POST',
    body: JSON.stringify({ lead_id: leadId })
  });
  const leadData = await leadResponse.json();

  // Build transaction request with customer's selections
  const response = await fetch('/transaction/add/', {
    method: 'POST',
    body: JSON.stringify({
      lead_id: leadId,
      created_by: userId,

      // Copy package-level data from lead
      package_snapshot: {
        name: leadData.package.name,
        description: leadData.package.description,
        type: leadData.package.type,
        pax_size: leadData.package.pax_size,
        no_of_days: leadData.package.no_of_days,
        inclusions: leadData.package.inclusions,
        exclusions: leadData.package.exclusions,
        amenities: leadData.package.amenities,
        policies: leadData.package.policies,
        images: leadData.package.images
      },

      // Map customer selections
      itinerary_selections: customerSelections.map(selection => ({
        day: selection.day,
        title: selection.title,
        description: selection.description,
        selected_hotel_id: selection.selectedHotelId,  // Customer's choice
        selected_car_dealer_id: selection.selectedTransportId,  // Customer's choice
        activities: selection.activities
      })),

      // Financial details
      base_amount: calculatedBaseAmount,
      discount_amount: discount,
      taxes: taxes,
      final_amount: finalAmount,
      amount_paid: initialPayment,
      amount_due: finalAmount - initialPayment,

      // Booking details
      travel_start_date: startDate,
      travel_end_date: endDate,
      booking_status: 'confirmed',
      payment_status: initialPayment > 0 ? 'partial' : 'unpaid',
      booking_notes: notes
    })
  });
};
```

### Step 2: Update UI for Customer Selection

You need to add a selection interface where customers can:

1. **View all hotel options** for each day (from lead's `hotel_details` array)
2. **Select ONE hotel** per day
3. **View all transport options** for each day (from lead's `car_dealer_details` array)
4. **Select ONE transport** per day

**Example UI Component:**
```javascript
// Display hotel options for a day
const HotelSelector = ({ day, hotelOptions, onSelect }) => {
  return (
    <div>
      <h3>Day {day} - Select Hotel</h3>
      {hotelOptions.map(hotel => (
        <div key={hotel.id} onClick={() => onSelect(hotel.id)}>
          <h4>{hotel.name}</h4>
          <p>{hotel.description}</p>
          <img src={hotel.images[0]?.image_url} />
        </div>
      ))}
    </div>
  );
};
```

### Step 3: Update Status Field Handling

**OLD:**
```javascript
status: "new" | "confirmed" | "cancelled"
```

**NEW:**
```javascript
booking_status: "pending" | "confirmed" | "cancelled" | "completed"
payment_status: "unpaid" | "partial" | "paid" | "refunded"
```

Update your status badges/filters to use both fields.

---

## Summary of Changes

| Aspect | OLD Transaction API | NEW Transaction API |
|--------|-------------------|-------------------|
| **Entry Point** | Direct from Package | Via Lead (required) |
| **Hotel/Transport** | Single option embedded | Customer selects from multiple options |
| **Request Field** | `itinerary_details` | `itinerary_selections` |
| **Hotel Format** | Full object `{id, name, ...}` | Just ID `selected_hotel_id: 4` |
| **Status Fields** | Single `status` | `booking_status` + `payment_status` |
| **Payment Tracking** | `final_amount` only | `amount_paid`, `amount_due` |
| **Timestamps** | `created_at` only | `created_at`, `updated_at`, `confirmed_at`, `cancelled_at` |

---

## Testing Checklist

- [ ] Can create a Lead with multiple hotel/transport options
- [ ] UI displays all options for customer to choose from
- [ ] Customer can select one hotel and one transport per day
- [ ] Transaction creation works with customer's selections
- [ ] Booking status updates correctly
- [ ] Payment status updates correctly
- [ ] Transaction displays customer's selected hotel/transport (not all options)

---

## Need Help?

Contact the backend team if you have questions about:
- Lead creation and structure
- Customer selection flow
- Transaction API integration
- Status field mapping


