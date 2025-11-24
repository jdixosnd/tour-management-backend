# Package Options API Documentation

## Overview
This document describes the multi-option packages feature that allows a Package to have multiple pricing options (e.g., Standard, Deluxe, Premium). Each option has:
- A specific price (amount)
- A specific set of hotels for each day of the itinerary
- The core itinerary (days, cities, activities) remains common across all options

## Database Schema

### New Tables

#### PackageOption
Stores different pricing/hotel options for a package.

| Field | Type | Description |
|-------|------|-------------|
| id | BigAutoField | Primary key |
| package | ForeignKey | Reference to Package |
| name | CharField(100) | Option name (e.g., 'Standard', 'Deluxe', 'Premium') |
| amount | Decimal(15,2) | Price for this option |
| description | TextField | Optional description |
| tour_operator | ForeignKey | Reference to Touroperator |
| created_by | ForeignKey | Reference to User |
| created_at | DateTimeField | Auto-generated timestamp |
| updated_at | DateTimeField | Auto-updated timestamp |

#### PackageOptionHotelMapping
Maps hotels to specific days for each package option.

| Field | Type | Description |
|-------|------|-------------|
| id | BigAutoField | Primary key |
| package_option | ForeignKey | Reference to PackageOption |
| hotel | ForeignKey | Reference to Hotel |
| day | Integer | Day number matching the itinerary |
| tour_operator | ForeignKey | Reference to Touroperator |
| selected_by | ForeignKey | Reference to User |
| created_at | DateTimeField | Auto-generated timestamp |

## API Endpoints

### 1. Add Package with Options

**Endpoint:** `POST /package/add/`

**Request Body:**
```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Kerala Tour",
  "type": "group",
  "destination_id": 1,
  "description": "Beautiful Kerala tour package",
  "pax_size": 4,
  "contains_travel_fare": true,
  "transport_type": "bus",
  "no_of_days": 3,
  "package_amount": 15000,
  "notes": "Best season: October to March",
  "terms_and_conditions": "Cancellation policy applies",
  "itinerary_items": [
    {
      "day": 1,
      "city": "Kochi",
      "state": "Kerala",
      "title": "Arrival in Kochi",
      "description": "Explore Fort Kochi",
      "note": "Check-in after 2 PM",
      "activities": [
        {
          "type": "sightseeing",
          "name": "Fort Kochi Beach",
          "description": "Visit the historic beach",
          "charges": 0,
          "sequence": 1,
          "location": {
            "city": "Kochi",
            "state": "Kerala",
            "country": "India",
            "name": "Fort Kochi",
            "address": "Fort Kochi Beach Road"
          }
        }
      ],
      "hotel_details": [101, 102],
      "car_dealers": [1]
    },
    {
      "day": 2,
      "city": "Munnar",
      "state": "Kerala",
      "title": "Munnar Sightseeing",
      "description": "Tea gardens and hills",
      "note": "Early morning departure",
      "activities": [],
      "hotel_details": [201, 202],
      "car_dealers": [1]
    }
  ],
  "inclusions": [
    {
      "name": "Accommodation",
      "description": "Hotel stay for all nights"
    }
  ],
  "exclusions": [
    {
      "name": "Personal Expenses",
      "description": "Shopping, laundry, etc."
    }
  ],
  "package_options": [
    {
      "name": "Standard",
      "amount": 15000,
      "description": "Budget-friendly option with standard hotels",
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [101]
        },
        {
          "day": 2,
          "hotel_ids": [201]
        }
      ]
    },
    {
      "name": "Deluxe",
      "amount": 22000,
      "description": "Mid-range option with deluxe hotels",
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [102]
        },
        {
          "day": 2,
          "hotel_ids": [202]
        }
      ]
    },
    {
      "name": "Premium",
      "amount": 35000,
      "description": "Luxury option with premium hotels",
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [102, 103]
        },
        {
          "day": 2,
          "hotel_ids": [202, 203]
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "message": "Package created successfully",
  "package_id": 14
}
```

### 2. Update Package with Options

**Endpoint:** `POST /package/update/`

**Request Body:** Same structure as Add Package, but include `"id": <package_id>` field.

**Response:**
```json
{
  "message": "Package updated successfully",
  "package_id": 14
}
```

### 3. Get Package with Options

**Endpoint:** `POST /package/get/`

**Request Body:**
```json
{
  "tour_operator_id": 1,
  "package_id": 14
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 14,
      "name": "Kerala Tour",
      "destination_id": 1,
      "description": "Beautiful Kerala tour package",
      "pax_size": 4,
      "contains_travel_fare": true,
      "transport_type": "bus",
      "no_of_days": 3,
      "package_amount": 15000.0,
      "is_active": true,
      "type": "group",
      "terms_and_conditions": "Cancellation policy applies",
      "itinerary_details": [
        {
          "day": 1,
          "city": "Kochi",
          "state": "Kerala",
          "title": "Arrival in Kochi",
          "description": "Explore Fort Kochi",
          "note": "Check-in after 2 PM",
          "activities": [...],
          "hotel_details": [...],
          "car_dealers": [...]
        }
      ],
      "inclusions": [...],
      "exclusions": [...],
      "images": [...],
      "package_options": [
        {
          "id": 1,
          "name": "Standard",
          "amount": 15000.0,
          "description": "Budget-friendly option with standard hotels",
          "hotel_mappings": [
            {
              "day": 1,
              "hotel_ids": [101]
            },
            {
              "day": 2,
              "hotel_ids": [201]
            }
          ]
        },
        {
          "id": 2,
          "name": "Deluxe",
          "amount": 22000.0,
          "description": "Mid-range option with deluxe hotels",
          "hotel_mappings": [
            {
              "day": 1,
              "hotel_ids": [102]
            },
            {
              "day": 2,
              "hotel_ids": [202]
            }
          ]
        },
        {
          "id": 3,
          "name": "Premium",
          "amount": 35000.0,
          "description": "Luxury option with premium hotels",
          "hotel_mappings": [
            {
              "day": 1,
              "hotel_ids": [102, 103]
            },
            {
              "day": 2,
              "hotel_ids": [202, 203]
            }
          ]
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

## Important Notes

### Backward Compatibility
- The `package_amount` field in the Package model is still supported for backward compatibility
- If `package_options` is not provided, the package will work with the legacy `package_amount` and `hotel_details` on itinerary items
- When `package_options` is provided, it takes precedence for pricing and hotel selection

### Data Structure
- Each package option has its own set of hotel mappings
- Hotel mappings are day-wise, allowing different hotels for different days
- Multiple hotels can be selected for a single day in an option (e.g., giving customers a choice)
- The core itinerary (activities, cities, days) remains the same across all options

### Frontend Implementation Guidelines

1. **Package Form:**
   - Keep the base `package_amount` field (optional, for backward compatibility)
   - Add a new "Package Options" section
   - Allow adding/removing multiple options
   - For each option:
     - Name field (required)
     - Amount field (required)
     - Description field (optional)
     - Hotel selection UI for each day (inheriting days from main itinerary)

2. **Package Display:**
   - Show available options as tabs or cards
   - Display price for each option
   - Show hotels corresponding to the selected option
   - Highlight differences between options

3. **Validation:**
   - Ensure at least one option is provided if using the new structure
   - Validate that hotel_ids in hotel_mappings exist and belong to the tour operator
   - Ensure day numbers in hotel_mappings match the itinerary days

## Migration Information

A database migration has been created and applied:
- Migration file: `0012_packageoption_packageoptionhotelmapping.py`
- Tables created: `PackageOption`, `PackageOptionHotelMapping`
- No data migration needed (new feature)

## Testing

To test the implementation:
1. Create a package with multiple options using the add API
2. Verify the package is created with all options
3. Update the package to modify options
4. Retrieve the package and verify all options are returned correctly
5. Test backward compatibility by creating a package without options

