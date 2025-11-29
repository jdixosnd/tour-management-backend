# Room Selection Feature - Frontend Integration Guide

## Overview
The system now supports room type and quantity selection when building packages, creating leads, and making bookings. This guide explains the API changes and how to integrate them.

---

## 1. Package Creation & Updates

### New Request Format
When creating or updating packages, you can now specify room selections for each hotel:

```javascript
const packageData = {
  name: "Kerala Delight",
  destination_id: 5,
  package_options: [
    {
      name: "Standard",
      amount: 50000,
      vehicle_type: "SUV",
      hotel_mappings: [
        {
          day: 1,
          hotel_ids: [
            {
              hotel_id: 10,
              selected_room_type_id: 25,  // NEW: Room type ID
              room_quantity: 2             // NEW: Number of rooms
            },
            {
              hotel_id: 11,
              selected_room_type_id: 30,
              room_quantity: 1
            }
          ],
          quick_hotels: [
            {
              hotel_name: "Budget Inn",
              room_type: "Deluxe",        // Already exists
              total_rooms: 2,              // Already exists
              price_per_night: 2000
            }
          ]
        }
      ]
    }
  ]
};
```

### Backward Compatibility
The old format still works (array of hotel IDs without room details):
```javascript
hotel_ids: [10, 11]  // ✅ Still supported
```

---

## 2. Package Response Format

### GET Package API Response
```javascript
{
  "id": 1,
  "name": "Kerala Delight",
  "package_options": [
    {
      "id": 5,
      "name": "Standard",
      "amount": 50000,
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [
            {
              "hotel_id": 10,
              "selected_room_type_id": 25,
              "room_quantity": 2,
              "selected_room_type": {      // NEW: Full room details
                "id": 25,
                "name": "Ocean View Suite",
                "type": "Suite",
                "capacity": 3,
                "bedtype": "King",
                "price_per_night": 5000,
                "description": "Spacious suite with ocean view"
              }
            }
          ],
          "quick_hotels": [...]
        }
      ]
    }
  ]
}
```

---

## 3. Lead Creation

### Request Format
When creating a lead, pass the package snapshot with room selections:

```javascript
const leadData = {
  tour_operator_id: 1,
  created_by: userId,
  customer_id: 123,
  status: "New",
  package_snapshot: {
    // Use the exact response from GET Package API
    // Room selections will be automatically captured and snapshotted
    ...packageData
  }
};
```

### Lead Response
The GET Lead API returns the same structure as Package API, including room selections.

---

## 4. Booking Creation

### Request Format
```javascript
const bookingData = {
  lead_id: 45,
  created_by: userId,
  itinerary_selections: [
    {
      day: 1,
      title: "Arrival in Kochi",
      description: "Check-in and relax",
      selected_hotel_id: 10,
      selected_room_type_id: 25,     // NEW: Selected room type
      room_quantity: 2,               // NEW: Number of rooms
      room_snapshot: {                // NEW: Room details snapshot
        "id": 25,
        "name": "Ocean View Suite",
        "type": "Suite",
        "capacity": 3,
        "bedtype": "King",
        "price_per_night": 5000,
        "description": "Spacious suite with ocean view"
      },
      vehicle_type: "SUV",
      activities: [...]
    }
  ],
  final_amount: 68500,
  travel_start_date: "2025-12-01",
  travel_end_date: "2025-12-05"
};
```

### Booking Response
```javascript
{
  "transaction_id": 78,
  "itinerary": [
    {
      "day": 1,
      "hotel": {
        "id": 10,
        "name": "Beach Resort",
        "selected_room_type_id": 25,    // NEW
        "room_quantity": 2,              // NEW
        "room_snapshot": {               // NEW: Complete room details
          "id": 25,
          "name": "Ocean View Suite",
          "type": "Suite",
          "capacity": 3,
          "bedtype": "King",
          "price_per_night": 5000
        }
      }
    }
  ]
}
```

---

## 5. Quick Hotels

Quick hotels already support room information through existing fields:
- `room_type`: String field for room type name
- `total_rooms`: Number of rooms

No changes needed for quick hotels.

---

## 6. Fetching Room Types for a Hotel

### New API Endpoint: `GET /hotel/room_types/get/`

Use this API to fetch available room types when building packages.

**Request:**
```javascript
const fetchRoomTypes = async (hotelId) => {
  const response = await fetch('/hotel/room_types/get/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tour_operator_id: 1,
      hotel_id: hotelId,
      include_binary: false  // Optional: set to true to get image binary data
    })
  });

  return await response.json();
};
```

**Response:**
```javascript
{
  "hotel_id": 10,
  "hotel_name": "Beach Resort",
  "room_types": [
    {
      "id": 25,
      "name": "Ocean View Suite",
      "type": "Suite",
      "capacity": 3,
      "bedtype": "King",
      "price_per_night": 5000.0,
      "description": "Spacious suite with ocean view",
      "rating": 4.5,
      "images": [...],
      "amenities": [...],
      "inclusions": [...],
      "exclusions": [...],
      "policies": [...]
    },
    {
      "id": 26,
      "name": "Deluxe Room",
      "type": "Deluxe",
      "capacity": 2,
      "bedtype": "Queen",
      "price_per_night": 3500.0,
      "description": "Comfortable deluxe room",
      "rating": 4.0,
      "images": [...],
      "amenities": [...],
      "inclusions": [...],
      "exclusions": [...],
      "policies": [...]
    }
  ]
}
```

---

## 7. UI Implementation Suggestions

### Package Builder
1. When user selects a hotel, call the room types API
2. Display available room types in a dropdown or card layout
3. Let user select room type from the list
4. Let user specify quantity (number input)
5. Display selected room details (type, capacity, price, images)

### Lead Creation
1. Copy room selections from package automatically
2. Allow editing if needed before creating lead

### Booking Creation
1. Show room selections from lead
2. Allow final confirmation/modification
3. Display total cost based on room quantity and price

**Example Implementation:**
```javascript
// When hotel is selected in package builder
const onHotelSelected = async (hotelId) => {
  const roomData = await fetchRoomTypes(hotelId);

  // Display room types to user
  setAvailableRooms(roomData.room_types);
};

// When user selects a room type
const onRoomTypeSelected = (roomTypeId, quantity) => {
  const selectedRoom = availableRooms.find(r => r.id === roomTypeId);

  // Add to package data
  const hotelSelection = {
    hotel_id: hotelId,
    selected_room_type_id: roomTypeId,
    room_quantity: quantity,
    selected_room_type: selectedRoom  // Include full details for display
  };

  // Add to hotel_mappings array
  addHotelToDay(currentDay, hotelSelection);
};
```

---

## 8. Migration Notes

- All existing packages, leads, and bookings continue to work
- Room selection fields are optional (nullable)
- Old format (array of IDs) is still supported for backward compatibility
- New features are additive, not breaking changes

---

## Questions?
Contact the backend team for any clarifications or issues.

