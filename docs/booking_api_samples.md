# Booking API - Sample Requests & Responses

Complete working examples for all 4 Booking APIs with real sample data.

---

## 1. Create Booking - `POST /booking/add/`

### Sample Request

```json
{
  "lead_id": 1,
  "created_by": 1,
  "package_snapshot": {
    "name": "Kerala Backwaters & Hill Stations",
    "description": "Experience the serene backwaters of Alleppey and the misty hills of Munnar in this 5-day Kerala tour",
    "type": "leisure",
    "pax_size": 4,
    "no_of_days": 5,
    "inclusions": [
      {
        "id": 1,
        "name": "Daily Breakfast",
        "description": "Complimentary breakfast at all hotels"
      },
      {
        "id": 2,
        "name": "Airport Transfers",
        "description": "Pick up and drop at Kochi airport"
      },
      {
        "id": 3,
        "name": "Sightseeing",
        "description": "All sightseeing as per itinerary"
      }
    ],
    "exclusions": [
      {
        "id": 1,
        "name": "Lunch & Dinner",
        "description": "Meals other than breakfast are not included"
      },
      {
        "id": 2,
        "name": "Personal Expenses",
        "description": "Shopping, tips, laundry, etc."
      }
    ],
    "amenities": [
      {
        "id": 1,
        "name": "Free WiFi",
        "description": "Complimentary WiFi at all hotels"
      },
      {
        "id": 2,
        "name": "Air Conditioning",
        "description": "AC rooms and vehicles"
      }
    ],
    "policies": [
      {
        "id": 1,
        "name": "Cancellation Policy",
        "description": "Free cancellation up to 7 days before travel. 50% refund for 3-7 days. No refund within 3 days."
      },
      {
        "id": 2,
        "name": "Payment Policy",
        "description": "30% advance required to confirm booking. Balance due 3 days before travel."
      }
    ],
    "images": [
      {
        "id": 1,
        "image_url": "https://example.com/images/kerala-backwaters.jpg",
        "caption": "Alleppey Backwaters"
      },
      {
        "id": 2,
        "image_url": "https://example.com/images/munnar-tea-gardens.jpg",
        "caption": "Munnar Tea Gardens"
      }
    ]
  },
  "itinerary_selections": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "description": "Arrive at Kochi International Airport. Transfer to hotel. Evening visit to Marine Drive and Lulu Mall.",
      "selected_hotel_id": 5,
      "selected_car_dealer_id": 3,
      "hotel_images": [
        {
          "id": 10,
          "image_url": "https://example.com/images/hotel-grand-kochi.jpg",
          "caption": "Hotel Grand Kochi - Deluxe Room"
        }
      ],
      "car_type": "Sedan - Toyota Etios",
      "activities": [
        {
          "id": 1,
          "name": "Airport Transfer",
          "description": "Pick up from Kochi airport"
        },
        {
          "id": 2,
          "name": "Marine Drive Visit",
          "description": "Evening stroll at Marine Drive"
        }
      ]
    },
    {
      "day": 2,
      "title": "Kochi Sightseeing",
      "description": "Full day Kochi sightseeing - Fort Kochi, Chinese Fishing Nets, Mattancherry Palace, Jewish Synagogue, Spice Market",
      "selected_hotel_id": 5,
      "selected_car_dealer_id": 3,
      "hotel_images": [],
      "car_type": "Sedan - Toyota Etios",
      "activities": [
        {
          "id": 3,
          "name": "Fort Kochi Tour",
          "description": "Guided tour of historic Fort Kochi area"
        },
        {
          "id": 4,
          "name": "Chinese Fishing Nets",
          "description": "Visit the iconic Chinese fishing nets"
        },
        {
          "id": 5,
          "name": "Mattancherry Palace",
          "description": "Explore the Dutch Palace"
        }
      ]
    },
    {
      "day": 3,
      "title": "Kochi to Munnar",
      "description": "Drive to Munnar (130 km, 4 hours). En route visit Cheeyappara and Valara waterfalls. Check in to hotel.",
      "selected_hotel_id": 8,
      "selected_car_dealer_id": 3,
      "hotel_images": [
        {
          "id": 15,
          "image_url": "https://example.com/images/munnar-resort.jpg",
          "caption": "Munnar Hill Resort - Valley View Room"
        }
      ],
      "car_type": "Sedan - Toyota Etios",
      "activities": [
        {
          "id": 6,
          "name": "Scenic Drive to Munnar",
          "description": "Beautiful drive through Western Ghats"
        },
        {
          "id": 7,
          "name": "Waterfall Stops",
          "description": "Photo stops at Cheeyappara and Valara waterfalls"
        }
      ]
    },
    {
      "day": 4,
      "title": "Munnar Sightseeing",
      "description": "Visit Tea Museum, Mattupetty Dam, Echo Point, Kundala Lake, and Tea Gardens",
      "selected_hotel_id": 8,
      "selected_car_dealer_id": 3,
      "hotel_images": [],
      "car_type": "Sedan - Toyota Etios",
      "activities": [
        {
          "id": 8,
          "name": "Tea Museum Visit",
          "description": "Learn about tea processing"
        },
        {
          "id": 9,
          "name": "Mattupetty Dam",
          "description": "Scenic dam and boating"
        },
        {
          "id": 10,
          "name": "Tea Garden Walk",
          "description": "Walk through lush tea plantations"
        }
      ]
    }
  ],
  "base_amount": 75000.00,
  "discount_amount": 5000.00,
  "taxes": 3500.00,
  "final_amount": 73500.00,
  "amount_paid": 22050.00,
  "amount_due": 51450.00,
  "travel_start_date": "2025-12-15",
  "travel_end_date": "2025-12-19",
  "booking_status": "confirmed",
  "payment_status": "partial",
  "booking_notes": "Customer requested early check-in at 11 AM on Day 1. Vegetarian meals preferred."
}
```

### Sample Response (Success)

```json
{
  "message": "Booking created successfully",
  "transaction_id": 42,
  "booking_id": 42
}
```

### Sample Response (Error - Missing Fields)

```json
{
  "error": "Missing required fields: lead_id, created_by"
}
```

### Sample Response (Error - Lead Not Found)

```json
{
  "error": "Lead with id 1 not found"
}
```

---

## 2. Get Booking Details - `POST /booking/get/`

### Sample Request

```json
{
  "transaction_id": 42
}
```

### Sample Response (Success)

```json
{
  "transaction_id": 42,
  "booking_id": 42,
  "lead_id": 1,
  "customer": {
    "id": 12,
    "name": "Rajesh Kumar",
    "email": "rajesh.kumar@example.com",
    "phone": "+91-9876543210"
  },
  "tour_operator": {
    "id": 2,
    "name": "Kerala Dream Holidays Pvt Ltd"
  },
  "destination": {
    "id": 5,
    "name": "Kerala"
  },
  "package": {
    "name": "Kerala Backwaters & Hill Stations",
    "description": "Experience the serene backwaters of Alleppey and the misty hills of Munnar in this 5-day Kerala tour",
    "type": "leisure",
    "pax_size": 4,
    "no_of_days": 5,
    "inclusions": [
      {
        "id": 1,
        "name": "Daily Breakfast",
        "description": "Complimentary breakfast at all hotels"
      },
      {
        "id": 2,
        "name": "Airport Transfers",
        "description": "Pick up and drop at Kochi airport"
      }
    ],
    "exclusions": [
      {
        "id": 1,
        "name": "Lunch & Dinner",
        "description": "Meals other than breakfast are not included"
      }
    ],
    "amenities": [
      {
        "id": 1,
        "name": "Free WiFi",
        "description": "Complimentary WiFi at all hotels"
      }
    ],
    "policies": [
      {
        "id": 1,
        "name": "Cancellation Policy",
        "description": "Free cancellation up to 7 days before travel"
      }
    ],
    "images": [
      {
        "id": 1,
        "image_url": "https://example.com/images/kerala-backwaters.jpg",
        "caption": "Alleppey Backwaters"
      }
    ]
  },
  "itinerary": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "description": "Arrive at Kochi International Airport. Transfer to hotel.",
      "hotel": {
        "id": 5,
        "name": "Hotel Grand Kochi",
        "description": "4-star business hotel in the heart of Kochi",
        "images": [
          {
            "id": 10,
            "image_url": "https://example.com/images/hotel-grand-kochi.jpg",
            "caption": "Hotel Grand Kochi - Deluxe Room"
          }
        ]
      },
      "transport": {
        "id": 3,
        "name": "Kerala Cabs & Tours",
        "car_type": "Sedan - Toyota Etios"
      },
      "activities": [
        {
          "id": 1,
          "name": "Airport Transfer",
          "description": "Pick up from Kochi airport"
        }
      ]
    },
    {
      "day": 2,
      "title": "Kochi Sightseeing",
      "description": "Full day Kochi sightseeing",
      "hotel": {
        "id": 5,
        "name": "Hotel Grand Kochi",
        "description": "4-star business hotel in the heart of Kochi",
        "images": []
      },
      "transport": {
        "id": 3,
        "name": "Kerala Cabs & Tours",
        "car_type": "Sedan - Toyota Etios"
      },
      "activities": [
        {
          "id": 3,
          "name": "Fort Kochi Tour",
          "description": "Guided tour of historic Fort Kochi area"
        }
      ]
    }
  ],
  "booking_status": "confirmed",
  "payment_status": "partial",
  "financial_details": {
    "base_amount": 75000.00,
    "discount_amount": 5000.00,
    "taxes": 3500.00,
    "final_amount": 73500.00,
    "amount_paid": 22050.00,
    "amount_due": 51450.00
  },
  "travel_dates": {
    "start_date": "2025-12-15",
    "end_date": "2025-12-19"
  },
  "booking_notes": "Customer requested early check-in at 11 AM on Day 1. Vegetarian meals preferred.",
  "cancellation_reason": null,
  "timestamps": {
    "created_at": "2025-11-13T14:30:25Z",
    "updated_at": "2025-11-13T14:30:25Z",
    "confirmed_at": "2025-11-13T14:30:25Z",
    "cancelled_at": null
  },
  "created_by": {
    "id": 1,
    "username": "admin"
  }
}
```

### Sample Response (Error - Not Found)

```json
{
  "error": "Booking with id 42 not found"
}
```

---


## 3. Get All Bookings - `POST /booking/get_all/`

### Sample Request (With All Filters)

```json
{
  "tour_operator": 2,
  "customer_id": 12,
  "booking_status": "confirmed",
  "payment_status": "partial",
  "destination_id": 5,
  "from_date": "2025-01-01",
  "to_date": "2025-12-31"
}
```

### Sample Request (No Filters - Get All)

```json
{}
```

### Sample Request (Filter by Status Only)

```json
{
  "booking_status": "pending"
}
```

### Sample Response (Success)

```json
{
  "bookings": [
    {
      "transaction_id": 42,
      "booking_id": 42,
      "lead_id": 1,
      "customer_id": 12,
      "customer_name": "Rajesh Kumar",
      "customer_email": "rajesh.kumar@example.com",
      "package_name": "Kerala Backwaters & Hill Stations",
      "destination": "Kerala",
      "booking_status": "confirmed",
      "payment_status": "partial",
      "base_amount": 75000.00,
      "final_amount": 73500.00,
      "amount_paid": 22050.00,
      "amount_due": 51450.00,
      "travel_start_date": "2025-12-15",
      "travel_end_date": "2025-12-19",
      "created_at": "2025-11-13T14:30:25Z",
      "confirmed_at": "2025-11-13T14:30:25Z"
    },
    {
      "transaction_id": 43,
      "booking_id": 43,
      "lead_id": 5,
      "customer_id": 15,
      "customer_name": "Priya Sharma",
      "customer_email": "priya.sharma@example.com",
      "package_name": "Goa Beach Paradise",
      "destination": "Goa",
      "booking_status": "confirmed",
      "payment_status": "paid",
      "base_amount": 55000.00,
      "final_amount": 52500.00,
      "amount_paid": 52500.00,
      "amount_due": 0.00,
      "travel_start_date": "2025-12-20",
      "travel_end_date": "2025-12-24",
      "created_at": "2025-11-12T10:15:30Z",
      "confirmed_at": "2025-11-12T10:15:30Z"
    },
    {
      "transaction_id": 44,
      "booking_id": 44,
      "lead_id": 8,
      "customer_id": 18,
      "customer_name": "Amit Patel",
      "customer_email": "amit.patel@example.com",
      "package_name": "Rajasthan Royal Heritage",
      "destination": "Rajasthan",
      "booking_status": "pending",
      "payment_status": "unpaid",
      "base_amount": 95000.00,
      "final_amount": 92000.00,
      "amount_paid": 0.00,
      "amount_due": 92000.00,
      "travel_start_date": "2026-01-10",
      "travel_end_date": "2026-01-17",
      "created_at": "2025-11-13T16:45:00Z",
      "confirmed_at": null
    }
  ],
  "total_count": 3
}
```

### Sample Response (Empty Results)

```json
{
  "bookings": [],
  "total_count": 0
}
```

---

## 4. Update Booking - `POST /booking/update/`

### Sample Request (Update Payment - Partial Payment)

```json
{
  "transaction_id": 42,
  "payment_status": "partial",
  "amount_paid": 45000.00,
  "amount_due": 28500.00,
  "booking_notes": "Customer paid additional ₹22,950 via UPI on 2025-11-14. Total paid: ₹45,000. Balance: ₹28,500."
}
```

### Sample Request (Update Payment - Full Payment)

```json
{
  "transaction_id": 42,
  "payment_status": "paid",
  "amount_paid": 73500.00,
  "amount_due": 0.00,
  "booking_notes": "Full payment received via bank transfer on 2025-11-15. Transaction ID: TXN123456789."
}
```

### Sample Request (Confirm Booking)

```json
{
  "transaction_id": 44,
  "booking_status": "confirmed",
  "booking_notes": "Booking confirmed after receiving advance payment. Hotels and transport reserved."
}
```

### Sample Request (Cancel Booking)

```json
{
  "transaction_id": 42,
  "booking_status": "cancelled",
  "cancellation_reason": "Customer unable to travel due to medical emergency. Refund processed as per cancellation policy.",
  "payment_status": "refunded"
}
```

### Sample Request (Complete Booking)

```json
{
  "transaction_id": 42,
  "booking_status": "completed",
  "booking_notes": "Trip completed successfully. Customer feedback: Excellent experience!"
}
```

### Sample Request (Update Travel Dates)

```json
{
  "transaction_id": 42,
  "travel_start_date": "2025-12-20",
  "travel_end_date": "2025-12-24",
  "booking_notes": "Travel dates changed as per customer request. Hotels and transport rescheduled."
}
```

### Sample Response (Success)

```json
{
  "message": "Booking updated successfully",
  "transaction_id": 42,
  "booking_id": 42
}
```

### Sample Response (Error - Not Found)

```json
{
  "error": "Booking with id 42 not found"
}
```

---

## Quick Reference - Common Scenarios

### Scenario 1: Customer Makes Advance Payment (30%)

**Request:**
```json
{
  "transaction_id": 42,
  "booking_status": "confirmed",
  "payment_status": "partial",
  "amount_paid": 22050.00,
  "amount_due": 51450.00,
  "booking_notes": "Advance payment (30%) received. Booking confirmed."
}
```

### Scenario 2: Customer Pays Balance Before Travel

**Request:**
```json
{
  "transaction_id": 42,
  "payment_status": "paid",
  "amount_paid": 73500.00,
  "amount_due": 0.00,
  "booking_notes": "Full payment completed. Ready for travel."
}
```

### Scenario 3: Customer Requests Cancellation

**Request:**
```json
{
  "transaction_id": 42,
  "booking_status": "cancelled",
  "cancellation_reason": "Personal reasons - family emergency",
  "payment_status": "refunded",
  "booking_notes": "Cancelled 10 days before travel. Full refund processed."
}
```

### Scenario 4: Trip Completed Successfully

**Request:**
```json
{
  "transaction_id": 42,
  "booking_status": "completed",
  "booking_notes": "Trip completed on 2025-12-19. Customer satisfied with services."
}
```

### Scenario 5: Filter Pending Bookings Awaiting Payment

**Request:**
```json
{
  "booking_status": "pending",
  "payment_status": "unpaid",
  "tour_operator": 2
}
```

### Scenario 6: Filter Confirmed Bookings with Partial Payment

**Request:**
```json
{
  "booking_status": "confirmed",
  "payment_status": "partial",
  "tour_operator": 2
}
```

---

## Testing Tips

### 1. Test Create Booking Flow

```bash
# Step 1: Create a lead first (use lead API)
# Step 2: Create booking from that lead
curl -X POST http://localhost:8000/booking/add/ \
  -H "Content-Type: application/json" \
  -d @booking_create_sample.json
```

### 2. Test Get Booking

```bash
curl -X POST http://localhost:8000/booking/get/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 42}'
```

### 3. Test List All Bookings

```bash
curl -X POST http://localhost:8000/booking/get_all/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 4. Test Update Payment

```bash
curl -X POST http://localhost:8000/booking/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": 42,
    "payment_status": "paid",
    "amount_paid": 73500.00,
    "amount_due": 0.00
  }'
```

---

## Notes

1. **All APIs use POST method** - Even for retrieving data
2. **All amounts are in decimal format** - Use 2 decimal places (e.g., 73500.00)
3. **Dates format** - Use YYYY-MM-DD format (e.g., "2025-12-15")
4. **Status values are case-sensitive** - Use lowercase (e.g., "confirmed", not "Confirmed")
5. **transaction_id and booking_id are the same** - Both refer to the Transaction table primary key
6. **lead_id is required** - Must create a Lead before creating a Booking
7. **itinerary_selections must match lead's itinerary** - Customer selects ONE hotel and ONE transport per day from lead options

---

## Status Reference

### Booking Status Values
- `pending` - Awaiting confirmation
- `confirmed` - Booking confirmed
- `cancelled` - Booking cancelled
- `completed` - Trip completed

### Payment Status Values
- `unpaid` - No payment received
- `partial` - Partial payment received
- `paid` - Fully paid
- `refunded` - Payment refunded

---

## Related Documentation

- **Complete API Reference:** `docs/booking_api_reference.md`
- **UI Implementation Guide:** `docs/transaction_api_update_for_ui.md`
- **Quick Reference:** `docs/transaction_api_quick_reference.md`
- **"Book Now" Button Guide:** `docs/booking_button_implementation.md`
