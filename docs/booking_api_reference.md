# Booking APIs - Complete Reference

## 📋 Overview

These are the **NEW working Booking APIs** that replace the deprecated transaction APIs. All booking APIs work with the Lead-based system.

**Base URL:** `http://your-domain/`

---

## ✅ Available APIs

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/booking/add/` | POST | Create new booking from lead | ✅ Working |
| `/booking/get/` | POST | Get booking details | ✅ Working |
| `/booking/get_all/` | POST | List all bookings with filters | ✅ Working |
| `/booking/update/` | POST | Update booking status/payment | ✅ Working |

**Deprecated APIs (DO NOT USE):**
- ❌ `/transaction/add/` - Returns HTTP 410 (Gone)
- ❌ `/transaction/get/` - Returns HTTP 410 (Gone)
- ❌ `/transaction/update/` - Returns HTTP 410 (Gone)

---

## 1. Create Booking

**Endpoint:** `POST /booking/add/`

**Description:** Create a new booking (transaction) from a Lead with customer's selected hotel and transport options.

### Request Body

```json
{
  "lead_id": 3,
  "created_by": 1,
  "package_snapshot": {
    "name": "Kerala Delight",
    "description": "5 days tour of Kerala backwaters and hill stations",
    "type": "leisure",
    "pax_size": 4,
    "no_of_days": 5,
    "inclusions": [
      {"id": 1, "name": "Breakfast", "description": "Daily breakfast"},
      {"id": 2, "name": "Airport Transfer", "description": "Pick up and drop"}
    ],
    "exclusions": [
      {"id": 1, "name": "Lunch", "description": "Lunch not included"},
      {"id": 2, "name": "Dinner", "description": "Dinner not included"}
    ],
    "amenities": [
      {"id": 1, "name": "WiFi", "description": "Free WiFi"},
      {"id": 2, "name": "AC", "description": "Air conditioning"}
    ],
    "policies": [
      {"id": 1, "name": "Cancellation", "description": "Free cancellation up to 7 days before travel"}
    ],
    "images": [
      {"id": 1, "image_url": "https://example.com/image1.jpg", "caption": "Kerala backwaters"}
    ]
  },
  "itinerary_selections": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "description": "Arrive at Kochi airport, transfer to hotel",
      "selected_hotel_id": 4,
      "selected_car_dealer_id": 2,
      "hotel_images": [
        {"id": 10, "image_url": "https://example.com/hotel1.jpg"}
      ],
      "car_type": "Sedan",
      "activities": [
        {"id": 1, "name": "Airport Transfer", "description": "Pick up from airport"}
      ]
    },
    {
      "day": 2,
      "title": "Kochi Sightseeing",
      "description": "Visit Fort Kochi, Chinese fishing nets",
      "selected_hotel_id": 4,
      "selected_car_dealer_id": 2,
      "hotel_images": [],
      "car_type": "Sedan",
      "activities": [
        {"id": 2, "name": "Fort Kochi Tour", "description": "Guided tour of Fort Kochi"},
        {"id": 3, "name": "Chinese Fishing Nets", "description": "Visit the famous fishing nets"}
      ]
    }
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
  "booking_notes": "Customer requested early check-in at 11 AM"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `lead_id` | Integer | ID of the lead being booked |
| `created_by` | Integer | ID of the user creating the booking |
| `itinerary_selections` | Array | Customer's selected hotels/transports per day |
| `final_amount` | Decimal | Total booking amount |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `package_snapshot` | Object | {} | Package details snapshot |
| `base_amount` | Decimal | 0 | Base package price |
| `discount_amount` | Decimal | 0 | Discount applied |
| `taxes` | Decimal | 0 | Tax amount |
| `amount_paid` | Decimal | 0 | Amount already paid |
| `amount_due` | Decimal | 0 | Remaining amount |
| `travel_start_date` | Date | null | Travel start date (YYYY-MM-DD) |
| `travel_end_date` | Date | null | Travel end date (YYYY-MM-DD) |
| `booking_status` | String | "pending" | "pending", "confirmed", "cancelled", "completed" |
| `payment_status` | String | "unpaid" | "unpaid", "partial", "paid", "refunded" |
| `booking_notes` | String | "" | Additional notes |

### Itinerary Selection Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `day` | Integer | Yes | Day number |
| `title` | String | No | Day title |
| `description` | String | No | Day description |
| `selected_hotel_id` | Integer | No | ID of selected hotel |
| `selected_car_dealer_id` | Integer | No | ID of selected transport |
| `hotel_images` | Array | No | Hotel images |
| `car_type` | String | No | Type of car |
| `activities` | Array | No | Activities for the day |

### Response (Success - 201)

```json
{
  "message": "Booking created successfully",
  "transaction_id": 15,
  "booking_id": 15
}
```

### Response (Error - 400)

```json
{
  "error": "Missing required fields: lead_id, created_by"
}
```

### Response (Error - 404)

```json
{
  "error": "Lead with id 3 not found"
}
```

---

## 2. Get Booking Details

**Endpoint:** `POST /booking/get/`

**Description:** Retrieve complete details of a specific booking.

### Request Body

```json
{
  "transaction_id": 15
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | Integer | ID of the booking to retrieve |

### Response (Success - 200)

```json
{
  "transaction_id": 15,
  "booking_id": 15,
  "lead_id": 3,
  "customer": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+91-9876543210"
  },
  "tour_operator": {
    "id": 1,
    "name": "Kerala Tours & Travels"
  },
  "destination": {
    "id": 2,
    "name": "Kerala"
  },
  "package": {
    "name": "Kerala Delight",
    "description": "5 days tour of Kerala backwaters and hill stations",
    "type": "leisure",
    "pax_size": 4,
    "no_of_days": 5,
    "inclusions": [
      {"id": 1, "name": "Breakfast", "description": "Daily breakfast"}
    ],
    "exclusions": [
      {"id": 1, "name": "Lunch", "description": "Lunch not included"}
    ],
    "amenities": [
      {"id": 1, "name": "WiFi", "description": "Free WiFi"}
    ],
    "policies": [
      {"id": 1, "name": "Cancellation", "description": "Free cancellation up to 7 days"}
    ],
    "images": [
      {"id": 1, "image_url": "https://example.com/image1.jpg", "caption": "Kerala backwaters"}
    ]
  },
  "itinerary": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "description": "Arrive at Kochi airport, transfer to hotel",
      "hotel": {
        "id": 4,
        "name": "Grand Hyatt Kochi",
        "description": "5-star luxury hotel",
        "images": [
          {"id": 10, "image_url": "https://example.com/hotel1.jpg"}
        ]
      },
      "transport": {
        "id": 2,
        "name": "Premium Car Rentals",
        "car_type": "Sedan"
      },
      "activities": [
        {"id": 1, "name": "Airport Transfer", "description": "Pick up from airport"}
      ]
    },
    {
      "day": 2,
      "title": "Kochi Sightseeing",
      "description": "Visit Fort Kochi, Chinese fishing nets",
      "hotel": {
        "id": 4,
        "name": "Grand Hyatt Kochi",
        "description": "5-star luxury hotel",
        "images": []
      },
      "transport": {
        "id": 2,
        "name": "Premium Car Rentals",
        "car_type": "Sedan"
      },
      "activities": [
        {"id": 2, "name": "Fort Kochi Tour", "description": "Guided tour"},
        {"id": 3, "name": "Chinese Fishing Nets", "description": "Visit fishing nets"}
      ]
    }
  ],
  "booking_status": "confirmed",
  "payment_status": "partial",
  "financial_details": {
    "base_amount": 70000.00,
    "discount_amount": 5000.00,
    "taxes": 3500.00,
    "final_amount": 68500.00,
    "amount_paid": 20000.00,
    "amount_due": 48500.00
  },
  "travel_dates": {
    "start_date": "2025-12-01",
    "end_date": "2025-12-05"
  },
  "booking_notes": "Customer requested early check-in at 11 AM",
  "cancellation_reason": null,
  "timestamps": {
    "created_at": "2025-11-13T10:30:00Z",
    "updated_at": "2025-11-13T10:30:00Z",
    "confirmed_at": "2025-11-13T10:30:00Z",
    "cancelled_at": null
  },
  "created_by": {
    "id": 1,
    "username": "admin"
  }
}
```

### Response (Error - 404)

```json
{
  "error": "Booking with id 15 not found"
}
```

---

## 3. Get All Bookings

**Endpoint:** `POST /booking/get_all/`

**Description:** Retrieve list of all bookings with optional filters.

### Request Body

```json
{
  "tour_operator": 1,
  "customer_id": 5,
  "booking_status": "confirmed",
  "payment_status": "partial",
  "destination_id": 2,
  "from_date": "2025-01-01",
  "to_date": "2025-12-31"
}
```

### Optional Filters

| Field | Type | Description |
|-------|------|-------------|
| `tour_operator` | Integer | Filter by tour operator ID |
| `customer_id` | Integer | Filter by customer ID |
| `booking_status` | String | Filter by booking status |
| `payment_status` | String | Filter by payment status |
| `destination_id` | Integer | Filter by destination ID |
| `from_date` | Date | Filter bookings from this date (YYYY-MM-DD) |
| `to_date` | Date | Filter bookings until this date (YYYY-MM-DD) |

**Note:** All filters are optional. If no filters provided, returns all bookings.


### Response (Success - 200)

```json
{
  "bookings": [
    {
      "transaction_id": 15,
      "booking_id": 15,
      "lead_id": 3,
      "customer_id": 5,
      "customer_name": "John Doe",
      "customer_email": "john@example.com",
      "package_name": "Kerala Delight",
      "destination": "Kerala",
      "booking_status": "confirmed",
      "payment_status": "partial",
      "base_amount": 70000.00,
      "final_amount": 68500.00,
      "amount_paid": 20000.00,
      "amount_due": 48500.00,
      "travel_start_date": "2025-12-01",
      "travel_end_date": "2025-12-05",
      "created_at": "2025-11-13T10:30:00Z",
      "confirmed_at": "2025-11-13T10:30:00Z"
    },
    {
      "transaction_id": 16,
      "booking_id": 16,
      "lead_id": 4,
      "customer_id": 6,
      "customer_name": "Jane Smith",
      "customer_email": "jane@example.com",
      "package_name": "Goa Beach Holiday",
      "destination": "Goa",
      "booking_status": "pending",
      "payment_status": "unpaid",
      "base_amount": 50000.00,
      "final_amount": 48000.00,
      "amount_paid": 0.00,
      "amount_due": 48000.00,
      "travel_start_date": "2025-12-15",
      "travel_end_date": "2025-12-20",
      "created_at": "2025-11-13T11:00:00Z",
      "confirmed_at": null
    }
  ],
  "total_count": 2
}
```

---

## 4. Update Booking

**Endpoint:** `POST /booking/update/`

**Description:** Update booking status, payment details, or other fields.

### Request Body

```json
{
  "transaction_id": 15,
  "booking_status": "confirmed",
  "payment_status": "paid",
  "amount_paid": 68500.00,
  "amount_due": 0.00,
  "booking_notes": "Payment completed. Customer confirmed arrival time.",
  "travel_start_date": "2025-12-05",
  "travel_end_date": "2025-12-10"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | Integer | ID of the booking to update |

### Optional Fields (Update any combination)

| Field | Type | Description |
|-------|------|-------------|
| `booking_status` | String | "pending", "confirmed", "cancelled", "completed" |
| `payment_status` | String | "unpaid", "partial", "paid", "refunded" |
| `amount_paid` | Decimal | Amount paid by customer |
| `amount_due` | Decimal | Remaining amount due |
| `booking_notes` | String | Additional notes |
| `cancellation_reason` | String | Reason for cancellation (if cancelling) |
| `travel_start_date` | Date | Travel start date (YYYY-MM-DD) |
| `travel_end_date` | Date | Travel end date (YYYY-MM-DD) |

**Note:** Only include fields you want to update. Other fields remain unchanged.

### Response (Success - 200)

```json
{
  "message": "Booking updated successfully",
  "transaction_id": 15,
  "booking_id": 15
}
```

### Response (Error - 404)

```json
{
  "error": "Booking with id 15 not found"
}
```

### Example: Cancel Booking

```json
{
  "transaction_id": 15,
  "booking_status": "cancelled",
  "cancellation_reason": "Customer requested cancellation due to personal reasons",
  "payment_status": "refunded"
}
```

### Example: Update Payment

```json
{
  "transaction_id": 15,
  "payment_status": "paid",
  "amount_paid": 68500.00,
  "amount_due": 0.00,
  "booking_notes": "Full payment received via bank transfer"
}
```

---

## Status Values Reference

### Booking Status

| Value | Description | When to Use |
|-------|-------------|-------------|
| `pending` | Booking not yet confirmed | Initial state, awaiting confirmation |
| `confirmed` | Booking confirmed | After customer confirms and/or payment received |
| `cancelled` | Booking cancelled | Customer or operator cancelled |
| `completed` | Trip completed | After travel dates have passed |

### Payment Status

| Value | Description | When to Use |
|-------|-------------|-------------|
| `unpaid` | No payment received | Initial state, no payment yet |
| `partial` | Partial payment received | Some amount paid, balance due |
| `paid` | Fully paid | Complete payment received |
| `refunded` | Payment refunded | After cancellation and refund |

---

## Common Use Cases

### Use Case 1: Create Booking from Lead

**Scenario:** Customer reviewed lead options and selected their preferences. Now creating booking.

**Steps:**
1. Customer selects ONE hotel per day from lead's hotel options
2. Customer selects ONE transport per day from lead's transport options
3. Customer enters payment details
4. Call `POST /booking/add/` with selections

**Example:**
```javascript
// Customer selected Hotel ID 4 and Transport ID 2 for all days
const bookingData = {
  lead_id: 3,
  created_by: 1,
  package_snapshot: lead.package,
  itinerary_selections: lead.itinerary_details.map(day => ({
    day: day.day,
    title: day.title,
    description: day.description,
    selected_hotel_id: 4,  // Customer's choice
    selected_car_dealer_id: 2,  // Customer's choice
    activities: day.activities
  })),
  final_amount: 68500.00,
  amount_paid: 20000.00,
  amount_due: 48500.00,
  booking_status: "confirmed",
  payment_status: "partial"
};
```

### Use Case 2: Record Payment

**Scenario:** Customer makes additional payment towards booking.

**Steps:**
1. Calculate new `amount_paid` and `amount_due`
2. Update `payment_status` if fully paid
3. Call `POST /booking/update/`

**Example:**
```json
{
  "transaction_id": 15,
  "amount_paid": 68500.00,
  "amount_due": 0.00,
  "payment_status": "paid",
  "booking_notes": "Full payment received on 2025-11-15"
}
```

### Use Case 3: Cancel Booking

**Scenario:** Customer wants to cancel their booking.

**Steps:**
1. Update booking status to "cancelled"
2. Add cancellation reason
3. Update payment status if refund issued
4. Call `POST /booking/update/`

**Example:**
```json
{
  "transaction_id": 15,
  "booking_status": "cancelled",
  "cancellation_reason": "Customer unable to travel due to medical emergency",
  "payment_status": "refunded"
}
```

### Use Case 4: List Pending Bookings

**Scenario:** View all bookings awaiting confirmation.

**Example:**
```json
{
  "booking_status": "pending",
  "tour_operator": 1
}
```

### Use Case 5: List Unpaid Bookings

**Scenario:** View all bookings with pending payments.

**Example:**
```json
{
  "payment_status": "unpaid",
  "tour_operator": 1
}
```

---

## Error Handling

All APIs return appropriate HTTP status codes:

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 200 | Success (GET/UPDATE) | Booking retrieved/updated successfully |
| 201 | Created | Booking created successfully |
| 400 | Bad Request | Missing required fields, invalid JSON |
| 404 | Not Found | Booking/Lead/User not found |
| 405 | Method Not Allowed | Using GET instead of POST |
| 500 | Server Error | Database error, unexpected exception |

### Error Response Format

```json
{
  "error": "Description of the error"
}
```

---

## Testing the APIs

### Using cURL

**Create Booking:**
```bash
curl -X POST http://localhost:8000/booking/add/ \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 3,
    "created_by": 1,
    "itinerary_selections": [...],
    "final_amount": 68500.00
  }'
```

**Get Booking:**
```bash
curl -X POST http://localhost:8000/booking/get/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 15}'
```

**Get All Bookings:**
```bash
curl -X POST http://localhost:8000/booking/get_all/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator": 1}'
```

**Update Booking:**
```bash
curl -X POST http://localhost:8000/booking/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": 15,
    "payment_status": "paid",
    "amount_paid": 68500.00
  }'
```

---

## Migration from Old Transaction APIs

If you were using the old transaction APIs, here's how to migrate:

| Old API | New API | Changes |
|---------|---------|---------|
| `POST /transaction/add/` | `POST /booking/add/` | • Requires `lead_id`<br>• Use `itinerary_selections` instead of `itinerary_details`<br>• Pass hotel/transport IDs, not full objects |
| `POST /transaction/get/` | `POST /booking/get/` | • Same request format<br>• Response structure updated |
| `POST /transaction/update/` | `POST /booking/update/` | • Same request format<br>• Supports new fields |

**Key Differences:**
1. Must create Lead first before creating booking
2. Itinerary uses `selected_hotel_id` and `selected_car_dealer_id` (IDs only)
3. Separate `booking_status` and `payment_status` fields
4. Better payment tracking with `amount_paid` and `amount_due`

---

## Support

For questions or issues:
- See full documentation: `docs/transaction_api_update_for_ui.md`
- See quick reference: `docs/transaction_api_quick_reference.md`
- See "Book Now" button guide: `docs/booking_button_implementation.md`
