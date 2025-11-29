# Get Room Types API

## Endpoint
**POST** `/hotel/room_types/get/`

## Description
Fetches all available room types for a specific hotel. This API is designed for use during package building to allow users to select room types and quantities.

## Request

### Headers
```
Content-Type: application/json
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tour_operator_id` | integer | Yes | ID of the tour operator |
| `hotel_id` | integer | Yes | ID of the hotel to fetch room types for |
| `include_binary` | boolean | No | Whether to include binary image data (default: false) |

### Example Request
```json
{
  "tour_operator_id": 1,
  "hotel_id": 10,
  "include_binary": false
}
```

## Response

### Success Response (200 OK)

```json
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
      "images": [
        {
          "id": 100,
          "url": "/media/rooms/ocean_suite.jpg",
          "caption": "Ocean view from balcony"
        }
      ],
      "amenities": [
        {
          "id": 1,
          "name": "WiFi",
          "description": "High-speed internet"
        },
        {
          "id": 2,
          "name": "Air Conditioning",
          "description": "Climate control"
        }
      ],
      "inclusions": [
        {
          "id": 10,
          "name": "Breakfast",
          "description": "Complimentary breakfast"
        }
      ],
      "exclusions": [
        {
          "id": 20,
          "name": "Minibar",
          "description": "Minibar charges extra"
        }
      ],
      "policies": [
        {
          "id": 30,
          "name": "Cancellation",
          "description": "Free cancellation up to 24 hours"
        }
      ]
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

### Error Responses

#### 400 Bad Request - Missing Fields
```json
{
  "error": "Missing required fields: tour_operator_id, hotel_id"
}
```

#### 404 Not Found - Tour Operator Not Found
```json
{
  "error": "Tour operator with id 999 not found"
}
```

#### 404 Not Found - Hotel Not Found
```json
{
  "error": "Hotel with id 10 not found for this tour operator"
}
```

#### 405 Method Not Allowed
```json
{
  "error": "Only POST method is allowed"
}
```

## Usage Example

### JavaScript/Fetch
```javascript
const fetchRoomTypes = async (tourOperatorId, hotelId) => {
  try {
    const response = await fetch('/hotel/room_types/get/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tour_operator_id: tourOperatorId,
        hotel_id: hotelId,
        include_binary: false
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.room_types;
  } catch (error) {
    console.error('Error fetching room types:', error);
    throw error;
  }
};

// Usage
const roomTypes = await fetchRoomTypes(1, 10);
console.log(`Found ${roomTypes.length} room types for hotel`);
```

## Notes

- The API verifies that the hotel belongs to the specified tour operator
- Room types are ordered by type and name
- All room details including amenities, policies, and images are included
- Set `include_binary: true` only if you need the actual binary image data (increases response size)

