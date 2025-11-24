# Package Options Feature - Frontend Integration Guide

**Release Date**: 2025-11-24  
**Version**: 1.0  
**Status**: ✅ Production Ready  
**Backward Compatible**: Yes

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What Changed](#what-changed)
3. [API Request Changes](#api-request-changes)
4. [API Response Changes](#api-response-changes)
5. [Before vs After Comparison](#before-vs-after-comparison)
6. [Frontend Implementation Guide](#frontend-implementation-guide)
7. [TypeScript Types](#typescript-types)
8. [UI/UX Recommendations](#uiux-recommendations)
9. [Code Examples](#code-examples)
10. [Validation Rules](#validation-rules)
11. [Migration Strategy](#migration-strategy)
12. [Common Issues & Solutions](#common-issues--solutions)
13. [Testing Checklist](#testing-checklist)

---

## 📋 Overview

The Package API has been enhanced to support **multiple pricing options** (e.g., Standard, Deluxe, Premium) for each package. Each option can have:
- Its own price
- Different hotels for each day of the itinerary
- The same core itinerary (days, cities, activities)

### Key Benefits:
- 📈 **Increased Revenue**: Offer premium options for higher margins
- 🎯 **Better Targeting**: Cater to different customer segments
- 💰 **Customer Choice**: Let customers choose their budget tier
- ✅ **Backward Compatible**: Existing packages continue to work

---

## 🔄 What Changed

### New Optional Field: `package_options`

**Affected APIs:**
- ✅ `POST /package/add/` - Accepts `package_options` array
- ✅ `POST /package/update/` - Accepts `package_options` array
- ✅ `POST /package/get/` - Returns `package_options` array
- ✅ `POST /package/get_packages_from_destination/` - Returns `package_options` array

**Important Notes:**
- `package_options` is **OPTIONAL** - not required for basic packages
- **Backward compatible** - old packages without options still work
- Legacy `package_amount` field is still supported

---

## 📤 API Request Changes

### 1. Add Package API (`POST /package/add/`)

#### New Request Structure

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
  "terms_and_conditions": "Cancellation policy applies",
  
  "itinerary_items": [
    {
      "day": 1,
      "city": "Kochi",
      "state": "Kerala",
      "title": "Arrival in Kochi",
      "description": "Explore Fort Kochi",
      "note": "Check-in after 2 PM",
      "activities": [1, 2, 3],
      "hotel_details": [101, 102, 103],
      "car_dealers": [1]
    },
    {
      "day": 2,
      "city": "Munnar",
      "state": "Kerala",
      "title": "Munnar Sightseeing",
      "description": "Tea gardens and hills",
      "note": "Early morning departure",
      "activities": [4, 5],
      "hotel_details": [201, 202, 203],
      "car_dealers": [1]
    },
    {
      "day": 3,
      "city": "Alleppey",
      "state": "Kerala",
      "title": "Backwaters",
      "description": "Houseboat experience",
      "activities": [6],
      "hotel_details": [301, 302],
      "car_dealers": [1]
    }
  ],
  
  "inclusions": [1, 2, 3],
  "exclusions": [1, 2],
  
  "package_options": [
    {
      "name": "Standard",
      "amount": 15000,
      "description": "Budget-friendly option with standard hotels",
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [101]},
        {"day": 2, "hotel_ids": [201]},
        {"day": 3, "hotel_ids": [301]}
      ]
    },
    {
      "name": "Deluxe",
      "amount": 22000,
      "description": "Mid-range option with deluxe hotels",
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [102]},
        {"day": 2, "hotel_ids": [202]},
        {"day": 3, "hotel_ids": [302]}
      ]
    },
    {
      "name": "Premium",
      "amount": 35000,
      "description": "Luxury option with premium hotels and multiple choices",
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [102, 103]},
        {"day": 2, "hotel_ids": [202, 203]},
        {"day": 3, "hotel_ids": [302]}
      ]
    }
  ]
}
```

#### Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `package_options` | Array | No | List of pricing options for the package |
| `package_options[].name` | String | Yes | Option name (e.g., "Standard", "Deluxe") |
| `package_options[].amount` | Number | Yes | Price for this option |
| `package_options[].description` | String | No | Description of the option |
| `package_options[].hotel_mappings` | Array | Yes | Day-wise hotel selections |
| `hotel_mappings[].day` | Integer | Yes | Day number (must match itinerary) |
| `hotel_mappings[].hotel_ids` | Array | Yes | Hotel IDs for this day |

#### Important Notes:
- `hotel_ids` must exist in the corresponding itinerary day's `hotel_details` array
- You can select multiple hotels for a single day (gives customers choice)
- All itinerary days should be covered in `hotel_mappings`

---

### 2. Update Package API (`POST /package/update/`)

#### Request Structure

Same as Add Package, but include the `id` field:

```json
{
  "id": 14,
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Updated Kerala Tour",
  "package_options": [
    {
      "name": "Standard",
      "amount": 16000,
      "description": "Updated budget option",
      "hotel_mappings": [...]
    }
  ]
}
```

#### ⚠️ Critical Update Behavior:
- When updating `package_options`, **ALL existing options are deleted and replaced**
- If you want to keep existing options, you must include them in the update request
- Option IDs will change after update (delete and recreate pattern)

---

### 3. Get Package API (`POST /package/get/`)

#### Request (No Changes)
```json
{
  "tour_operator_id": 1,
  "package_id": 14
}
```

---

## 📥 API Response Changes

### Get Package & Get Packages from Destination Response

Both APIs now include a `package_options` array in each package object:

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
          "activities": [
            {
              "id": 1,
              "name": "Fort Kochi Walk",
              "description": "Explore historic Fort Kochi"
            }
          ],
          "hotel_details": [
            {
              "id": 101,
              "name": "Budget Beach Hotel",
              "ratings": 3,
              "address": "Fort Kochi",
              "amenities": ["WiFi", "Breakfast"]
            },
            {
              "id": 102,
              "name": "Deluxe Resort",
              "ratings": 4,
              "address": "Marine Drive",
              "amenities": ["WiFi", "Pool", "Spa"]
            },
            {
              "id": 103,
              "name": "Luxury Palace Hotel",
              "ratings": 5,
              "address": "MG Road",
              "amenities": ["WiFi", "Pool", "Spa", "Gym", "Restaurant"]
            }
          ],
          "car_dealers": [...]
        },
        {
          "day": 2,
          "city": "Munnar",
          "state": "Kerala",
          "title": "Munnar Sightseeing",
          "description": "Tea gardens and hills",
          "note": "Early morning departure",
          "activities": [...],
          "hotel_details": [
            {
              "id": 201,
              "name": "Hill View Hotel",
              "ratings": 3
            },
            {
              "id": 202,
              "name": "Tea Garden Resort",
              "ratings": 4
            },
            {
              "id": 203,
              "name": "Premium Mountain Resort",
              "ratings": 5
            }
          ],
          "car_dealers": [...]
        },
        {
          "day": 3,
          "city": "Alleppey",
          "state": "Kerala",
          "title": "Backwaters",
          "description": "Houseboat experience",
          "activities": [...],
          "hotel_details": [
            {
              "id": 301,
              "name": "Backwater Inn",
              "ratings": 3
            },
            {
              "id": 302,
              "name": "Luxury Houseboat Resort",
              "ratings": 5
            }
          ],
          "car_dealers": [...]
        }
      ],

      "inclusions": [
        {
          "id": 1,
          "name": "Accommodation",
          "description": "Hotel stays as per itinerary"
        },
        {
          "id": 2,
          "name": "Meals",
          "description": "Breakfast and dinner"
        }
      ],

      "exclusions": [
        {
          "id": 1,
          "name": "Airfare",
          "description": "Flight tickets not included"
        }
      ],

      "images": [
        {
          "id": 1,
          "image_url": "https://example.com/image1.jpg"
        }
      ],

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
            },
            {
              "day": 3,
              "hotel_ids": [301]
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
            },
            {
              "day": 3,
              "hotel_ids": [302]
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
            },
            {
              "day": 3,
              "hotel_ids": [302]
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

#### Response Field Details

| Field | Type | Description |
|-------|------|-------------|
| `package_options` | Array | List of all pricing options (empty array if none) |
| `package_options[].id` | Integer | Unique ID of the option |
| `package_options[].name` | String | Option name |
| `package_options[].amount` | Float | Price for this option |
| `package_options[].description` | String | Description of the option |
| `package_options[].hotel_mappings` | Array | Day-wise hotel selections |
| `hotel_mappings[].day` | Integer | Day number |
| `hotel_mappings[].hotel_ids` | Array | List of hotel IDs for this day |

---

## 🔄 Before vs After Comparison

### Request Structure

#### ❌ BEFORE (Old Format - Still Supported)

```json
{
  "name": "Kerala Tour",
  "no_of_days": 3,
  "package_amount": 15000,
  "itinerary_items": [
    {
      "day": 1,
      "city": "Kochi",
      "hotel_details": [101]
    },
    {
      "day": 2,
      "city": "Munnar",
      "hotel_details": [201]
    }
  ]
}
```

**Limitations:**
- ❌ Only ONE price for the entire package
- ❌ Only ONE hotel per day
- ❌ No flexibility for different customer budgets

---

#### ✅ AFTER (New Format - Recommended)

```json
{
  "name": "Kerala Tour",
  "no_of_days": 3,
  "package_amount": 15000,
  "itinerary_items": [
    {
      "day": 1,
      "city": "Kochi",
      "hotel_details": [101, 102, 103]
    },
    {
      "day": 2,
      "city": "Munnar",
      "hotel_details": [201, 202, 203]
    }
  ],
  "package_options": [
    {
      "name": "Standard",
      "amount": 15000,
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [101]},
        {"day": 2, "hotel_ids": [201]}
      ]
    },
    {
      "name": "Deluxe",
      "amount": 22000,
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [102]},
        {"day": 2, "hotel_ids": [202]}
      ]
    },
    {
      "name": "Premium",
      "amount": 35000,
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [103]},
        {"day": 2, "hotel_ids": [203]}
      ]
    }
  ]
}
```

**Benefits:**
- ✅ MULTIPLE pricing options
- ✅ Different hotels for each option
- ✅ Flexibility for different budgets
- ✅ Better customer choice

---

## 🎨 Frontend Implementation Guide

### Step 1: Update Package Form

Add a new section for "Package Options" in your package creation/edit form.

#### Recommended UI Structure:

```
┌─────────────────────────────────────────────────┐
│ Package Details                                 │
│ Name: [Kerala Tour                        ]     │
│ Days: [3]  Pax: [4]  Type: [Group ▼]           │
│                                                 │
│ ┌─ Itinerary ─────────────────────────────┐    │
│ │ Day 1: Kochi                             │    │
│ │   Hotels: [Hotel A, Hotel B, Hotel C]    │    │
│ │ Day 2: Munnar                            │    │
│ │   Hotels: [Hotel X, Hotel Y, Hotel Z]    │    │
│ │ Day 3: Alleppey                          │    │
│ │   Hotels: [Hotel P, Hotel Q]             │    │
│ └──────────────────────────────────────────┘    │
│                                                 │
│ ┌─ Package Options ───────────────────────┐    │
│ │                                          │    │
│ │ ┌─ Option 1 ─────────────────────────┐  │    │
│ │ │ Name: [Standard              ]     │  │    │
│ │ │ Price: [15000                ]     │  │    │
│ │ │ Description: [Budget-friendly...]  │  │    │
│ │ │                                    │  │    │
│ │ │ Hotel Selection by Day:            │  │    │
│ │ │ Day 1: [Hotel A ▼]                 │  │    │
│ │ │ Day 2: [Hotel X ▼]                 │  │    │
│ │ │ Day 3: [Hotel P ▼]                 │  │    │
│ │ │                        [Remove]    │  │    │
│ │ └────────────────────────────────────┘  │    │
│ │                                          │    │
│ │ ┌─ Option 2 ─────────────────────────┐  │    │
│ │ │ Name: [Deluxe                ]     │  │    │
│ │ │ Price: [22000                ]     │  │    │
│ │ │ Description: [Mid-range...]        │  │    │
│ │ │                                    │  │    │
│ │ │ Hotel Selection by Day:            │  │    │
│ │ │ Day 1: [Hotel B ▼]                 │  │    │
│ │ │ Day 2: [Hotel Y ▼]                 │  │    │
│ │ │ Day 3: [Hotel Q ▼]                 │  │    │
│ │ │                        [Remove]    │  │    │
│ │ └────────────────────────────────────┘  │    │
│ │                                          │    │
│ │ [+ Add Option]                           │    │
│ └──────────────────────────────────────────┘    │
│                                                 │
│ [Save Package]                                  │
└─────────────────────────────────────────────────┘
```

---

### Step 2: Update Package Display

Show options as selectable cards/tabs for users to choose from.

#### Recommended UI:

```
┌─────────────────────────────────────────────────┐
│ Kerala Tour - 3 Days                            │
├─────────────────────────────────────────────────┤
│ Choose Your Package Option:                     │
│                                                 │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│ │Standard │  │ Deluxe  │  │ Premium │         │
│ │₹15,000  │  │ ₹22,000 │  │ ₹35,000 │         │
│ │⭐⭐⭐    │  │ ⭐⭐⭐⭐  │  │ ⭐⭐⭐⭐⭐ │         │
│ │Budget   │  │ Comfort │  │ Luxury  │         │
│ │Hotels   │  │ Hotels  │  │ Hotels  │         │
│ │[Select] │  │[Select] │  │[Select] │ ✓       │
│ └─────────┘  └─────────┘  └─────────┘         │
├─────────────────────────────────────────────────┤
│ Selected: Premium (₹35,000)                     │
│                                                 │
│ ┌─ Day 1: Kochi ──────────────────────────┐    │
│ │ 🏨 Hotel: Luxury Palace Hotel ⭐⭐⭐⭐⭐    │    │
│ │    📍 MG Road, Kochi                     │    │
│ │    ✨ WiFi, Pool, Spa, Gym, Restaurant   │    │
│ │ 🚗 Transport: AC Bus                     │    │
│ │ 📍 Activities:                           │    │
│ │    • Fort Kochi Walk                     │    │
│ │    • Beach Sunset                        │    │
│ └──────────────────────────────────────────┘    │
│                                                 │
│ ┌─ Day 2: Munnar ─────────────────────────┐    │
│ │ 🏨 Hotel: Premium Mountain Resort ⭐⭐⭐⭐⭐│    │
│ │    📍 Tea Estate Road, Munnar            │    │
│ │    ✨ WiFi, Pool, Spa, Mountain View     │    │
│ │ 🚗 Transport: AC Bus                     │    │
│ │ 📍 Activities:                           │    │
│ │    • Tea Garden Tour                     │    │
│ │    • Viewpoint Visit                     │    │
│ └──────────────────────────────────────────┘    │
│                                                 │
│ ┌─ Day 3: Alleppey ───────────────────────┐    │
│ │ 🏨 Hotel: Luxury Houseboat Resort ⭐⭐⭐⭐⭐│    │
│ │    📍 Backwaters, Alleppey               │    │
│ │    ✨ WiFi, Houseboat, Backwater View    │    │
│ │ 🚗 Transport: AC Bus                     │    │
│ │ 📍 Activities:                           │    │
│ │    • Houseboat Cruise                    │    │
│ └──────────────────────────────────────────┘    │
│                                                 │
│ [Book Premium Package - ₹35,000]                │
└─────────────────────────────────────────────────┘
```

---

## 💻 TypeScript Types

```typescript
interface PackageOption {
  id?: number;              // Only in response
  name: string;             // Required: "Standard", "Deluxe", etc.
  amount: number;           // Required: Price for this option
  description?: string;     // Optional: Description
  hotel_mappings: HotelMapping[];
}

interface HotelMapping {
  day: number;              // Day number (1, 2, 3, ...)
  hotel_ids: number[];      // Array of hotel IDs for this day
}

interface ItineraryItem {
  day: number;
  city: string;
  state: string;
  title: string;
  description: string;
  note?: string;
  activities: number[];
  hotel_details: number[];  // Available hotels for this day
  car_dealers: number[];
}

interface Package {
  id?: number;
  name: string;
  destination_id: number;
  description: string;
  pax_size: number;
  contains_travel_fare: boolean;
  transport_type: string;
  no_of_days: number;
  package_amount: number;   // Legacy field (still supported)
  is_active?: boolean;
  type: string;
  terms_and_conditions?: string;
  itinerary_items: ItineraryItem[];
  inclusions: number[];
  exclusions: number[];
  package_options?: PackageOption[];  // New field (optional)
}

interface PackageResponse {
  data: Package[];
  pagination: {
    count: number;
    num_pages: number;
    current_page: number;
    next: string | null;
    previous: string | null;
  };
}
```

---

## 🎨 Code Examples

### React Example 1: Package Options Form Component

```jsx
import React, { useState } from 'react';

const PackageOptionsForm = ({ itineraryDays, availableHotels, onSave }) => {
  const [options, setOptions] = useState([]);

  const addOption = () => {
    setOptions([...options, {
      name: '',
      amount: 0,
      description: '',
      hotel_mappings: itineraryDays.map(day => ({
        day: day.day,
        hotel_ids: []
      }))
    }]);
  };

  const removeOption = (index) => {
    setOptions(options.filter((_, i) => i !== index));
  };

  const updateOption = (index, field, value) => {
    const updated = [...options];
    updated[index][field] = value;
    setOptions(updated);
  };

  const updateHotelMapping = (optionIndex, day, hotelIds) => {
    const updated = [...options];
    const mappingIndex = updated[optionIndex].hotel_mappings.findIndex(
      m => m.day === day
    );
    updated[optionIndex].hotel_mappings[mappingIndex].hotel_ids = hotelIds;
    setOptions(updated);
  };

  const getHotelsForDay = (day) => {
    const dayItinerary = itineraryDays.find(d => d.day === day);
    return dayItinerary?.hotel_details || [];
  };

  return (
    <div className="package-options-form">
      <h3>Package Options</h3>

      {options.map((option, optionIndex) => (
        <div key={optionIndex} className="option-form-card">
          <h4>Option {optionIndex + 1}</h4>

          <div className="form-group">
            <label>Option Name *</label>
            <input
              type="text"
              placeholder="e.g., Standard, Deluxe, Premium"
              value={option.name}
              onChange={(e) => updateOption(optionIndex, 'name', e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Price *</label>
            <input
              type="number"
              placeholder="15000"
              value={option.amount}
              onChange={(e) => updateOption(optionIndex, 'amount', parseFloat(e.target.value))}
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              placeholder="Brief description of this option"
              value={option.description}
              onChange={(e) => updateOption(optionIndex, 'description', e.target.value)}
              rows={3}
            />
          </div>

          <div className="hotel-selection-section">
            <h5>Hotel Selection by Day</h5>
            {itineraryDays.map(day => {
              const availableHotelsForDay = getHotelsForDay(day.day);
              const selectedHotels = option.hotel_mappings.find(
                m => m.day === day.day
              )?.hotel_ids || [];

              return (
                <div key={day.day} className="day-hotel-selection">
                  <label>Day {day.day} - {day.city}</label>
                  <select
                    multiple
                    value={selectedHotels}
                    onChange={(e) => {
                      const selected = Array.from(
                        e.target.selectedOptions,
                        opt => parseInt(opt.value)
                      );
                      updateHotelMapping(optionIndex, day.day, selected);
                    }}
                    className="hotel-multiselect"
                  >
                    {availableHotelsForDay.map(hotelId => {
                      const hotel = availableHotels.find(h => h.id === hotelId);
                      return (
                        <option key={hotelId} value={hotelId}>
                          {hotel?.name || `Hotel ${hotelId}`}
                          {hotel?.ratings && ` (${hotel.ratings}⭐)`}
                        </option>
                      );
                    })}
                  </select>
                  <small>Hold Ctrl/Cmd to select multiple hotels</small>
                </div>
              );
            })}
          </div>

          <button
            type="button"
            onClick={() => removeOption(optionIndex)}
            className="btn-remove"
          >
            Remove Option
          </button>
        </div>
      ))}

      <button type="button" onClick={addOption} className="btn-add">
        + Add Option
      </button>

      <button
        type="button"
        onClick={() => onSave(options)}
        className="btn-save"
        disabled={options.length === 0}
      >
        Save Options
      </button>
    </div>
  );
};

export default PackageOptionsForm;
```

---

### React Example 2: Package Options Display Component

```jsx
import React, { useState } from 'react';

const PackageOptionsDisplay = ({ packageData }) => {
  const [selectedOption, setSelectedOption] = useState(
    packageData.package_options?.[0] || null
  );

  // If no options, show legacy single-price view
  if (!packageData.package_options || packageData.package_options.length === 0) {
    return (
      <div className="package-single-price">
        <h3>Package Price</h3>
        <div className="price-display">
          <span className="amount">₹{packageData.package_amount.toLocaleString()}</span>
          <span className="per-person">per person</span>
        </div>
      </div>
    );
  }

  // Get hotel details for selected option
  const getHotelForDay = (day) => {
    if (!selectedOption) return null;

    const mapping = selectedOption.hotel_mappings.find(m => m.day === day);
    if (!mapping || mapping.hotel_ids.length === 0) return null;

    const dayItinerary = packageData.itinerary_details.find(d => d.day === day);
    if (!dayItinerary) return null;

    // Get the first hotel (or show multiple if available)
    const hotelId = mapping.hotel_ids[0];
    return dayItinerary.hotel_details.find(h => h.id === hotelId);
  };

  return (
    <div className="package-options-display">
      <h3>Choose Your Package Option</h3>

      {/* Options Cards */}
      <div className="options-grid">
        {packageData.package_options.map(option => (
          <div
            key={option.id}
            className={`option-card ${selectedOption?.id === option.id ? 'selected' : ''}`}
            onClick={() => setSelectedOption(option)}
          >
            <div className="option-header">
              <h4>{option.name}</h4>
              {selectedOption?.id === option.id && (
                <span className="selected-badge">✓ Selected</span>
              )}
            </div>

            <div className="option-price">
              <span className="amount">₹{option.amount.toLocaleString()}</span>
              <span className="per-person">per person</span>
            </div>

            {option.description && (
              <p className="option-description">{option.description}</p>
            )}

            <button
              className={`btn-select ${selectedOption?.id === option.id ? 'selected' : ''}`}
            >
              {selectedOption?.id === option.id ? 'Selected' : 'Select'}
            </button>
          </div>
        ))}
      </div>

      {/* Selected Option Details */}
      {selectedOption && (
        <div className="selected-option-details">
          <h3>Your Itinerary - {selectedOption.name} Package</h3>
          <p className="total-price">Total: ₹{selectedOption.amount.toLocaleString()}</p>

          {packageData.itinerary_details.map(day => {
            const hotel = getHotelForDay(day.day);

            return (
              <div key={day.day} className="day-card">
                <div className="day-header">
                  <h4>Day {day.day}: {day.city}</h4>
                  <span className="day-title">{day.title}</span>
                </div>

                {hotel && (
                  <div className="hotel-info">
                    <div className="hotel-icon">🏨</div>
                    <div className="hotel-details">
                      <h5>{hotel.name}</h5>
                      {hotel.ratings && (
                        <div className="ratings">
                          {'⭐'.repeat(hotel.ratings)}
                        </div>
                      )}
                      {hotel.address && (
                        <p className="address">📍 {hotel.address}</p>
                      )}
                      {hotel.amenities && hotel.amenities.length > 0 && (
                        <div className="amenities">
                          <span>✨ {hotel.amenities.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="day-description">
                  <p>{day.description}</p>
                  {day.note && <p className="note">📝 {day.note}</p>}
                </div>

                {day.activities && day.activities.length > 0 && (
                  <div className="activities">
                    <h6>Activities:</h6>
                    <ul>
                      {day.activities.map(activity => (
                        <li key={activity.id}>
                          📍 {activity.name}
                          {activity.description && ` - ${activity.description}`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}

          <button className="btn-book">
            Book {selectedOption.name} Package - ₹{selectedOption.amount.toLocaleString()}
          </button>
        </div>
      )}
    </div>
  );
};

export default PackageOptionsDisplay;
```

---

### React Example 3: Backward Compatibility Handler

```jsx
const PackageDisplay = ({ packageData }) => {
  // Check if package has options
  const hasOptions = packageData.package_options &&
                     packageData.package_options.length > 0;

  if (hasOptions) {
    // New format: Show options
    return <PackageOptionsDisplay packageData={packageData} />;
  } else {
    // Old format: Show single price
    return <PackageSinglePriceDisplay packageData={packageData} />;
  }
};

const PackageSinglePriceDisplay = ({ packageData }) => {
  return (
    <div className="package-legacy">
      <h2>{packageData.name}</h2>
      <div className="price-box">
        <span className="price">₹{packageData.package_amount.toLocaleString()}</span>
        <span className="duration">{packageData.no_of_days} Days</span>
      </div>

      {/* Show itinerary with single hotel per day */}
      {packageData.itinerary_details.map(day => (
        <div key={day.day} className="day-card">
          <h4>Day {day.day}: {day.city}</h4>
          {day.hotel_details && day.hotel_details[0] && (
            <div className="hotel">
              🏨 {day.hotel_details[0].name}
            </div>
          )}
          <p>{day.description}</p>
        </div>
      ))}

      <button className="btn-book">
        Book Now - ₹{packageData.package_amount.toLocaleString()}
      </button>
    </div>
  );
};
```

---

### JavaScript Example: Form Validation

```javascript
const validatePackageOptions = (options, itineraryItems) => {
  const errors = [];

  if (!options || options.length === 0) {
    // Options are optional, so this is not an error
    return { valid: true, errors: [] };
  }

  options.forEach((option, index) => {
    // Validate option name
    if (!option.name || option.name.trim() === '') {
      errors.push(`Option ${index + 1}: Name is required`);
    }

    if (option.name && option.name.length > 100) {
      errors.push(`Option ${index + 1}: Name must be less than 100 characters`);
    }

    // Validate amount
    if (!option.amount || option.amount <= 0) {
      errors.push(`Option ${index + 1}: Amount must be greater than 0`);
    }

    if (option.amount > 999999999999.99) {
      errors.push(`Option ${index + 1}: Amount is too large`);
    }

    // Validate hotel mappings
    if (!option.hotel_mappings || option.hotel_mappings.length === 0) {
      errors.push(`Option ${index + 1}: Hotel mappings are required`);
    } else {
      // Check if all days are covered
      const mappedDays = option.hotel_mappings.map(m => m.day);
      const itineraryDays = itineraryItems.map(item => item.day);

      itineraryDays.forEach(day => {
        if (!mappedDays.includes(day)) {
          errors.push(`Option ${index + 1}: Missing hotel mapping for day ${day}`);
        }
      });

      // Validate each mapping
      option.hotel_mappings.forEach(mapping => {
        const dayItinerary = itineraryItems.find(item => item.day === mapping.day);

        if (!dayItinerary) {
          errors.push(`Option ${index + 1}: Invalid day ${mapping.day} in hotel mapping`);
          return;
        }

        if (!mapping.hotel_ids || mapping.hotel_ids.length === 0) {
          errors.push(`Option ${index + 1}: At least one hotel must be selected for day ${mapping.day}`);
        }

        // Check if hotel IDs exist in itinerary
        mapping.hotel_ids.forEach(hotelId => {
          if (!dayItinerary.hotel_details.includes(hotelId)) {
            errors.push(
              `Option ${index + 1}: Hotel ID ${hotelId} not found in day ${mapping.day} itinerary`
            );
          }
        });
      });
    }

    // Check for duplicate option names
    const duplicates = options.filter(opt => opt.name === option.name);
    if (duplicates.length > 1) {
      errors.push(`Option ${index + 1}: Duplicate option name "${option.name}"`);
    }
  });

  return {
    valid: errors.length === 0,
    errors
  };
};

// Usage
const handleSubmit = (formData) => {
  const validation = validatePackageOptions(
    formData.package_options,
    formData.itinerary_items
  );

  if (!validation.valid) {
    alert('Validation errors:\n' + validation.errors.join('\n'));
    return;
  }

  // Submit the form
  submitPackage(formData);
};
```

---

### JavaScript Example: API Integration

```javascript
// Add Package with Options
const createPackageWithOptions = async (packageData) => {
  try {
    const response = await fetch('/package/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tour_operator_id: 1,
        created_by: 1,
        name: packageData.name,
        destination_id: packageData.destination_id,
        no_of_days: packageData.no_of_days,
        pax_size: packageData.pax_size,
        package_amount: packageData.package_amount,
        itinerary_items: packageData.itinerary_items,
        inclusions: packageData.inclusions,
        exclusions: packageData.exclusions,
        package_options: packageData.package_options, // New field
      }),
    });

    const result = await response.json();

    if (response.ok) {
      console.log('Package created successfully:', result);
      return result;
    } else {
      console.error('Error creating package:', result.error);
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Network error:', error);
    throw error;
  }
};

// Update Package with Options
const updatePackageWithOptions = async (packageId, packageData) => {
  try {
    // First, fetch current package to preserve existing options if needed
    const currentPackage = await fetchPackage(packageId);

    const response = await fetch('/package/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: packageId,
        tour_operator_id: 1,
        created_by: 1,
        ...packageData,
        // Include package_options - will replace all existing options
        package_options: packageData.package_options || currentPackage.package_options,
      }),
    });

    const result = await response.json();

    if (response.ok) {
      console.log('Package updated successfully:', result);
      return result;
    } else {
      console.error('Error updating package:', result.error);
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Network error:', error);
    throw error;
  }
};

// Fetch Package
const fetchPackage = async (packageId) => {
  try {
    const response = await fetch('/package/get/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tour_operator_id: 1,
        package_id: packageId,
      }),
    });

    const result = await response.json();

    if (response.ok && result.data && result.data.length > 0) {
      const packageData = result.data[0];
      console.log('Package fetched:', packageData);
      console.log('Package options:', packageData.package_options);
      return packageData;
    } else {
      throw new Error('Package not found');
    }
  } catch (error) {
    console.error('Error fetching package:', error);
    throw error;
  }
};
```

---

## ✅ Validation Rules

### Frontend Validation Checklist

#### 1. Option Name
- ✅ **Required**: Must not be empty
- ✅ **Max Length**: 100 characters
- ✅ **Unique**: Should be unique within the package
- ✅ **Descriptive**: Encourage meaningful names (e.g., "Standard", "Deluxe", not "Option 1")

#### 2. Option Amount
- ✅ **Required**: Must not be empty
- ✅ **Positive**: Must be greater than 0
- ✅ **Maximum**: 999,999,999,999.99
- ✅ **Format**: Valid decimal number

#### 3. Hotel Mappings
- ✅ **Complete Coverage**: Must include all days from the itinerary
- ✅ **At Least One Hotel**: Each day must have at least one hotel selected
- ✅ **Valid Hotel IDs**: Hotel IDs must exist in the corresponding itinerary day's `hotel_details`
- ✅ **Valid Day Numbers**: Day numbers must match the itinerary days

#### 4. General
- ✅ **At Least One Option**: If `package_options` is provided, it should have at least one option
- ✅ **No Duplicate Names**: Option names should be unique within the package

### Validation Example

```javascript
const validationRules = {
  optionName: {
    required: true,
    maxLength: 100,
    pattern: /^[a-zA-Z0-9\s-]+$/,
    message: 'Option name is required and must be alphanumeric'
  },
  optionAmount: {
    required: true,
    min: 0.01,
    max: 999999999999.99,
    message: 'Amount must be between 0.01 and 999,999,999,999.99'
  },
  hotelMappings: {
    required: true,
    minItems: 1,
    message: 'At least one hotel must be selected for each day'
  }
};
```

---

## 🔄 Migration Strategy

### Phase 1: Support Both Formats (Current State)

Your frontend should handle both old and new formats seamlessly.

```javascript
function displayPackage(packageData) {
  const hasOptions = packageData.package_options &&
                     packageData.package_options.length > 0;

  if (hasOptions) {
    // New format: Show options
    return renderPackageWithOptions(packageData);
  } else {
    // Old format: Show single price
    return renderPackageWithSinglePrice(packageData);
  }
}
```

### Phase 2: Encourage Migration

Add UI hints to encourage users to add options to existing packages:

```jsx
{!package.package_options && (
  <div className="migration-banner">
    <div className="banner-content">
      <h4>💡 Upgrade Your Package</h4>
      <p>Add package options to offer different pricing tiers to your customers!</p>
      <button onClick={handleAddOptions} className="btn-upgrade">
        Add Options
      </button>
    </div>
  </div>
)}
```

### Phase 3: Gradual Adoption

- **Week 1-2**: Deploy with backward compatibility
- **Week 3-4**: Monitor usage and gather feedback
- **Month 2**: Encourage users to add options to popular packages
- **Month 3+**: Most packages should have options

### Phase 4: Full Adoption (Future - Optional)

Eventually, you may want to make options mandatory for new packages:

```javascript
const validateNewPackage = (packageData) => {
  if (!packageData.package_options || packageData.package_options.length === 0) {
    return {
      valid: false,
      error: 'Please add at least one package option (e.g., Standard, Deluxe)'
    };
  }
  return { valid: true };
};
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Hotel IDs Not Matching

**Problem**: Selected hotel IDs in `hotel_mappings` don't exist in itinerary `hotel_details`

**Error Message**:
```json
{
  "error": "Hotel ID 999 not found in day 1 itinerary"
}
```

**Solution**:
```javascript
// Validate before submitting
const validateHotelMappings = (options, itineraryItems) => {
  for (const option of options) {
    for (const mapping of option.hotel_mappings) {
      const dayItinerary = itineraryItems.find(item => item.day === mapping.day);

      if (!dayItinerary) {
        throw new Error(`Day ${mapping.day} not found in itinerary`);
      }

      const invalidHotels = mapping.hotel_ids.filter(
        id => !dayItinerary.hotel_details.includes(id)
      );

      if (invalidHotels.length > 0) {
        throw new Error(
          `Invalid hotel IDs for day ${mapping.day}: ${invalidHotels.join(', ')}`
        );
      }
    }
  }
};
```

---

### Issue 2: Missing Days in Hotel Mappings

**Problem**: Not all itinerary days are covered in `hotel_mappings`

**Solution**:
```javascript
// Auto-generate mappings for all days
const generateHotelMappings = (itineraryItems) => {
  return itineraryItems.map(item => ({
    day: item.day,
    hotel_ids: [] // User will select later
  }));
};

// When adding a new option
const addNewOption = () => {
  const newOption = {
    name: '',
    amount: 0,
    description: '',
    hotel_mappings: generateHotelMappings(itineraryItems)
  };
  setOptions([...options, newOption]);
};
```

---

### Issue 3: Options Lost After Update

**Problem**: Existing options are deleted when updating package without including them

**Solution**: Always fetch current options before updating
```javascript
const updatePackage = async (packageId, updates) => {
  // Fetch current package
  const currentPackage = await fetchPackage(packageId);

  // Merge with updates, preserving options if not provided
  const updatedData = {
    ...currentPackage,
    ...updates,
    package_options: updates.package_options || currentPackage.package_options
  };

  // Submit update
  await submitPackageUpdate(packageId, updatedData);
};
```

---

### Issue 4: Empty Package Options Array

**Problem**: Sending `package_options: []` might cause confusion

**Solution**: Don't send the field if there are no options
```javascript
const preparePackageData = (formData) => {
  const packageData = {
    ...formData
  };

  // Only include package_options if there are actual options
  if (formData.package_options && formData.package_options.length > 0) {
    packageData.package_options = formData.package_options;
  } else {
    delete packageData.package_options;
  }

  return packageData;
};
```

---

### Issue 5: Displaying Hotels for Selected Option

**Problem**: Difficulty mapping hotel IDs to hotel details

**Solution**: Create a helper function
```javascript
const getHotelDetailsForOption = (option, itineraryDetails) => {
  return option.hotel_mappings.map(mapping => {
    const dayItinerary = itineraryDetails.find(d => d.day === mapping.day);

    if (!dayItinerary) return null;

    const hotels = mapping.hotel_ids.map(hotelId =>
      dayItinerary.hotel_details.find(h => h.id === hotelId)
    ).filter(Boolean);

    return {
      day: mapping.day,
      city: dayItinerary.city,
      hotels: hotels
    };
  }).filter(Boolean);
};

// Usage
const selectedOptionHotels = getHotelDetailsForOption(
  selectedOption,
  packageData.itinerary_details
);
```

---

### Issue 6: Multiple Hotels Per Day Display

**Problem**: How to display when multiple hotels are selected for one day

**Solution**: Show as options/alternatives
```jsx
{mapping.hotel_ids.length > 1 ? (
  <div className="hotel-options">
    <p>Choose from:</p>
    <ul>
      {mapping.hotel_ids.map(hotelId => {
        const hotel = getHotelById(hotelId, dayItinerary.hotel_details);
        return (
          <li key={hotelId}>
            {hotel.name} ({hotel.ratings}⭐)
          </li>
        );
      })}
    </ul>
  </div>
) : (
  <div className="single-hotel">
    {getHotelById(mapping.hotel_ids[0], dayItinerary.hotel_details).name}
  </div>
)}
```

---

## 🧪 Testing Checklist

### Manual Testing

#### Test Case 1: Create Package with Options
- [ ] Create a package with 2-3 options
- [ ] Verify each option has different prices
- [ ] Verify each option has different hotels
- [ ] Check that the package is created successfully
- [ ] Fetch the package and verify options are returned

#### Test Case 2: Create Package without Options
- [ ] Create a package without `package_options` field
- [ ] Verify it works with legacy `package_amount`
- [ ] Fetch the package and verify it returns empty `package_options` array

#### Test Case 3: Update Package Options
- [ ] Create a package with options
- [ ] Update the package with modified options
- [ ] Verify old options are replaced with new ones
- [ ] Verify option IDs change after update

#### Test Case 4: Display Package with Options
- [ ] Fetch a package with options
- [ ] Display options as cards/tabs
- [ ] Select different options
- [ ] Verify hotels change based on selected option

#### Test Case 5: Validation
- [ ] Try creating option without name (should fail)
- [ ] Try creating option with negative amount (should fail)
- [ ] Try creating option with invalid hotel IDs (should fail)
- [ ] Try creating option without hotel mappings (should fail)

#### Test Case 6: Edge Cases
- [ ] Package with 1 option
- [ ] Package with 10+ options
- [ ] Option with multiple hotels per day
- [ ] Option with same hotel for all days
- [ ] Very long option names/descriptions

### Automated Testing

```javascript
describe('Package Options', () => {
  test('should create package with options', async () => {
    const packageData = {
      name: 'Test Package',
      no_of_days: 2,
      itinerary_items: [
        { day: 1, city: 'City A', hotel_details: [1, 2] },
        { day: 2, city: 'City B', hotel_details: [3, 4] }
      ],
      package_options: [
        {
          name: 'Standard',
          amount: 10000,
          hotel_mappings: [
            { day: 1, hotel_ids: [1] },
            { day: 2, hotel_ids: [3] }
          ]
        }
      ]
    };

    const result = await createPackage(packageData);
    expect(result.success).toBe(true);
    expect(result.data.package_options).toHaveLength(1);
  });

  test('should validate hotel IDs', () => {
    const options = [{
      name: 'Standard',
      amount: 10000,
      hotel_mappings: [
        { day: 1, hotel_ids: [999] } // Invalid ID
      ]
    }];

    const itinerary = [
      { day: 1, hotel_details: [1, 2] }
    ];

    const validation = validatePackageOptions(options, itinerary);
    expect(validation.valid).toBe(false);
    expect(validation.errors).toContain(
      expect.stringContaining('Hotel ID 999 not found')
    );
  });
});
```

---

## 📊 Summary Table

| Aspect | Details |
|--------|---------|
| **New Field** | `package_options` (array, optional) |
| **Backward Compatible** | ✅ Yes |
| **Affected APIs** | add, update, get, get_packages_from_destination |
| **Required Changes** | Add form fields, update display logic |
| **Optional Changes** | Enhanced UI, validation, migration prompts |
| **Testing Required** | Create, update, display, validation |

---

## 🎯 Quick Reference

### Minimum Request (Add/Update):
```json
{
  "package_options": [
    {
      "name": "Standard",
      "amount": 15000,
      "hotel_mappings": [
        {"day": 1, "hotel_ids": [101]},
        {"day": 2, "hotel_ids": [201]}
      ]
    }
  ]
}
```

### Response Format (Get):
```json
{
  "data": [{
    "package_options": [
      {
        "id": 1,
        "name": "Standard",
        "amount": 15000.0,
        "description": "Budget option",
        "hotel_mappings": [
          {"day": 1, "hotel_ids": [101]},
          {"day": 2, "hotel_ids": [201]}
        ]
      }
    ]
  }]
}
```

---

## 📞 Support

### Questions or Issues?

1. **Check this document** for examples and solutions
2. **Test with sample data** using the provided examples
3. **Review validation rules** to ensure correct data format
4. **Contact backend team** with specific error messages if issues persist

### Reporting Bugs

Include:
- Request payload (JSON)
- Response received
- Expected behavior
- Actual behavior
- Screenshots (if UI-related)

---

**Last Updated**: 2025-11-24
**Version**: 1.0
**Status**: ✅ Production Ready

---

**Happy Coding! 🚀**
