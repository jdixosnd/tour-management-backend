# Package API - Sample Request & Response

## Update Package API

### Endpoint
```
POST /package/update/
```

### Sample Request Body

```json
{
  "id": 14,
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Malaysia Adventure Package",
  "destination_id": 2,
  "description": "Explore the beauty of Malaysia with this amazing package",
  "pax_size": 2,
  "contains_travel_fare": 1,
  "transport_type": "FLIGHT",
  "no_of_days": 2,
  "package_amount": 11111.0,
  "is_active": true,
  "type": "Adventure",
  "terms_and_conditions": "<div>\n    <h3>Terms &amp; Conditions</h3>\n    <p>By booking this package, you agree to the following terms:</p>\n    <ul>\n        <li><strong>Booking &amp; Payment:</strong> A non-refundable deposit is required upon booking. Full payment is due 30 days prior to departure. Prices are subject to change until full payment is received.</li>\n        <li><strong>Cancellation Policy:</strong> Cancellations must be in writing.\n            <ul>\n                <li>30+ days before departure: Forfeiture of deposit.</li>\n                <li>15-29 days before departure: 50% of total package cost.</li>\n                <li>14 days or less before departure: 100% of total package cost (non-refundable).</li>\n            </ul>\n        </li>\n        <li><strong>Travel Documents:</strong> You are responsible for ensuring all travelers have a valid passport (with at least 6 months validity from return date) and any necessary visas or health certificates for entry into Malaysia.</li>\n        <li><strong>No Refunds for Unused Services:</strong> No refunds or reductions will be made for any unused accommodation, meals, sightseeing tours, transport, or other services included in the package.</li>\n        <li><strong>Travel Insurance:</strong> We strongly recommend you purchase comprehensive travel insurance to cover cancellation, medical expenses, baggage loss, and other unforeseen events.</li>\n        <li><strong>Liability:</strong> We act as an agent for suppliers (airlines, hotels, transport) and are not liable for any injury, damage, loss, delay, or irregularity caused by these suppliers or by force majeure events (e.g., weather, natural disasters).</li>\n    </ul>\n    <p><strong>Note:</strong> These are summary terms. Full terms and conditions will be provided upon booking.</p>\n</div>",
  "itinerary_items": [
    {
      "day": 1,
      "city": "Kuala Lumpur",
      "state": "Selangor",
      "title": "Arrival Day",
      "description": "Arrive in Kuala Lumpur and check into hotel",
      "note": "Please arrive at hotel by 2 PM for check-in",
      "activities": [],
      "hotel_details": [1, 2],
      "car_dealers": [1]
    },
    {
      "day": 2,
      "city": "Kuala Lumpur",
      "state": "Selangor",
      "title": "City Tour",
      "description": "Full day city tour of Kuala Lumpur",
      "note": "Breakfast included at hotel",
      "activities": [
        {
          "name": "Petronas Twin Towers Visit",
          "type": "sightseeing",
          "description": "Visit the iconic Petronas Twin Towers",
          "charges": 50.0,
          "contact_no": "+60123456789",
          "sequence": 1,
          "location": {
            "city": "Kuala Lumpur",
            "state": "Selangor",
            "name": "Petronas Twin Towers",
            "address": "Kuala Lumpur City Centre",
            "country": "Malaysia"
          }
        },
        {
          "name": "Cultural Dance Show",
          "type": "event",
          "description": "Traditional Malaysian cultural dance performance",
          "charges": 30.0,
          "contact_no": "+60123456790",
          "sequence": 2,
          "location": {
            "city": "Kuala Lumpur",
            "state": "Selangor",
            "name": "Cultural Center",
            "address": "Jalan Ampang",
            "country": "Malaysia"
          }
        }
      ],
      "hotel_details": [1, 2],
      "car_dealers": [1]
    }
  ],
  "inclusions": [
    {
      "name": "Accommodation",
      "description": "4-star hotel accommodation for all nights"
    },
    {
      "name": "Meals",
      "description": "Daily breakfast and dinner included"
    },
    {
      "name": "Transportation",
      "description": "Airport transfers and all sightseeing transportation"
    }
  ],
  "exclusions": [
    {
      "name": "Airfare",
      "description": "International flight tickets not included"
    },
    {
      "name": "Personal Expenses",
      "description": "Shopping, laundry, and other personal expenses"
    }
  ]
}
```

### Key Points for Update Request

1. **Required Fields:**
   - `id` - Package ID to update
   - `tour_operator_id` - Tour operator ID
   - `created_by` - User ID who is updating
   - `name` - Package name
   - `type` - Package type
   - `destination_id` - Destination ID
   - `itinerary_items` - Array of itinerary items (NOT `itinerary_details`)

2. **Itinerary Items Structure:**
   - Each day must have: `day`, `city`, `state`, `title`, `description`, `note`
   - `activities` - Array of activity objects with location details
   - `hotel_details` - Array of hotel IDs (e.g., `[1, 2]`)
   - `car_dealers` - Array of car dealer IDs (e.g., `[1]`)

3. **Activities:**
   - Must include `location` object with: `city`, `state`, `name`, `address`, `country`
   - `type` must be either "event" or "sightseeing"
   - `sequence` determines the order of activities

4. **Inclusions/Exclusions:**
   - Only need `name` and `description` (no `id` field needed)

---

## Get Package API Response

### Endpoint
```
POST /package/get/
```

### Request Body
```json
{
  "tour_operator_id": 1,
  "package_id": 14
}
```

### Sample Response

```json
{
  "data": [
    {
      "id": 14,
      "name": "Malaysia Adventure Package",
      "destination_id": 2,
      "description": "Explore the beauty of Malaysia with this amazing package",
      "pax_size": 2,
      "contains_travel_fare": 1,
      "transport_type": "FLIGHT",
      "no_of_days": 2,
      "package_amount": 11111.0,
      "is_active": true,
      "type": "Adventure",
      "terms_and_conditions": "<div>...</div>",
      "itinerary_details": [
        {
          "day": 1,
          "city": "Kuala Lumpur",
          "state": "Selangor",
          "title": "Arrival Day",
          "description": "Arrive in Kuala Lumpur and check into hotel",
          "note": "Please arrive at hotel by 2 PM for check-in",
          "activities": [],
          "hotel_details": [
            {
              "id": 1,
              "name": "Grand Hotel KL",
              "location": {...},
              "rating": 4.5,
              "images": [...]
            }
          ],
          "car_dealers": [
            {
              "id": 1,
              "dealer_name": "WheelsOnJoy",
              "contact_no": "9898989898",
              "transport_types": [
                {
                  "name": "Toyota Camry",
                  "type": "Sedan"
                },
                {
                  "name": "Honda CR-V",
                  "type": "SUV"
                }
              ]
            }
          ]
        },
        {
          "day": 2,
          "city": "Kuala Lumpur",
          "state": "Selangor",
          "title": "City Tour",
          "description": "Full day city tour of Kuala Lumpur",
          "note": "Breakfast included at hotel",
          "activities": [
            {
              "name": "Petronas Twin Towers Visit",
              "type": "sightseeing",
              "description": "Visit the iconic Petronas Twin Towers",
              "charges": 50.0,
              "contact_no": "+60123456789",
              "sequence": 1,
              "location": {
                "id": 5,
                "city": "Kuala Lumpur",
                "state": "Selangor",
                "name": "Petronas Twin Towers",
                "address": "Kuala Lumpur City Centre",
                "country": "Malaysia"
              },
              "image_ids": [201, 202],
              "images": [
                {
                  "id": 201,
                  "description": "Towers view",
                  "order": 1,
                  "image_url": "/media/images/2024/01/15/towers.jpg"
                }
              ]
            }
          ],
          "hotel_details": [...],
          "car_dealers": [...]
        }
      ],
      "inclusions": [
        {
          "id": 16,
          "name": "Accommodation",
          "description": "4-star hotel accommodation for all nights"
        }
      ],
      "exclusions": [
        {
          "id": 9,
          "name": "Airfare",
          "description": "International flight tickets not included"
        }
      ],
      "images": [
        {
          "id": 101,
          "description": "Package cover image",
          "order": 1,
          "image_url": "/media/images/2024/01/15/package_cover.jpg"
        },
        {
          "id": 102,
          "description": "Destination view",
          "order": 2,
          "image_url": "/media/images/2024/01/15/destination.jpg"
        }
      ]
    }
  ],
  "pagination": {
    "count": 1,
    "num_pages": 1,
    "current_page": 1,
    "next": null,
    "previous": null
  }
}
```

### Key Differences Between Request and Response

| Field | Request (Update) | Response (Get) |
|-------|------------------|----------------|
| Itinerary | `itinerary_items` | `itinerary_details` |
| Hotel Details | Array of IDs: `[1, 2]` | Array of objects with full details |
| Car Dealers | Array of IDs: `[1]` | Array of objects with full details including `id` |
| Activities Location | Location object required | Location object with `id` included |
| Inclusions | No `id` field | Includes `id` field |
| Exclusions | No `id` field | Includes `id` field |
| Images | Not in request | Array of image objects |

---

## Important Notes

1. **Car Dealers in Response:**
   - Now includes `id` field for each car dealer
   - Use these IDs when updating the package

2. **Images:**
   - Images are managed separately via image upload/delete APIs
   - GET response includes all package images
   - UPDATE request does not include images field

3. **Transformation Required:**
   - When using GET response data for UPDATE, you need to transform:
     - `itinerary_details` → `itinerary_items`
     - Hotel objects → Hotel IDs
     - Car dealer objects → Car dealer IDs
     - Remove `images` field (manage separately)

