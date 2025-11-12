# Destination API Documentation

## Overview

The Destination API provides endpoints to manage tour destinations and their associated locations. Destinations represent travel locations that can have multiple associated geographic locations with detailed information including addresses, coordinates, and other metadata.

## Table of Contents

1. [Data Models](#data-models)
2. [API Endpoints](#api-endpoints)
   - [Add Destination](#1-add-destination)
   - [Get Destinations](#2-get-destinations)
3. [Image Management](#image-management)
   - [Upload Images](#upload-images)
   - [Get Images](#get-images)
   - [Delete Images](#delete-images)
4. [Relationship with Location](#relationship-with-location)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Data Models

### Destination Model

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Auto-generated primary key | Auto |
| `tour_operator_id` | ForeignKey | Reference to tour operator | Yes |
| `created_by` | ForeignKey | Reference to user who created | Yes |
| `name` | String(255) | Name of the destination | Yes |
| `description` | Text | Description of the destination | No |
| `created_at` | DateTime | Auto-generated timestamp | Auto |
| `image_ids` | JSONField | Array of image IDs | No |

### Location Model

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | BigInteger | Auto-generated primary key | Auto |
| `tour_operator` | ForeignKey | Reference to tour operator | No |
| `created_by` | ForeignKey | Reference to user who created | No |
| `name` | String(255) | Name of the location | Yes |
| `city` | String(255) | City name | No |
| `state` | String(255) | State/province name | No |
| `country` | String(255) | Country name | No |
| `pin_code` | String(255) | Postal/ZIP code | No |
| `address` | Text(1024) | Full address | No |
| `lng` | Decimal(10,7) | Longitude coordinate | No |
| `lat` | Decimal(10,7) | Latitude coordinate | No |
| `created_at` | DateTime | Auto-generated timestamp | Auto |

### StateCity Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | BigInteger | Auto-generated primary key |
| `state` | String(255) | State/province name |
| `city` | String(255) | City name |

### StateCityToDestinationMapping Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | BigInteger | Auto-generated primary key |
| `state_city` | ForeignKey | Reference to StateCity |
| `destination` | ForeignKey | Reference to Destination |
| `location` | ForeignKey | Reference to Location (nullable) |

---

## API Endpoints

### 1. Add Destination

Creates a new destination with associated location(s).

#### Endpoint
```
POST /destination/add/
```

#### Method Name
`add_destination(request)`

#### Request Headers
```
Content-Type: application/json
```

#### Request Body

```json
{
  "tour_operator_id": integer,
  "user_id": integer,
  "name": string,
  "description": string (optional),
  "locations": [
    {
      // Option 1: Reference existing location
      "location_id": integer
    },
    // OR Option 2: Create new location with full details
    {
      "city": string,
      "state": string,
      "country": string (optional),
      "name": string (optional),
      "address": string (optional),
      "pin_code": string (optional),
      "lat": float (optional),
      "lng": float (optional)
    }
  ]
}
```

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tour_operator_id` | integer | Yes | ID of the tour operator |
| `user_id` | integer | Yes | ID of the user creating the destination |
| `name` | string | Yes | Name of the destination |
| `description` | string | No | Description of the destination |
| `locations` | array | Yes | Array of location objects (at least one required) |

**Location Object Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location_id` | integer | Conditional* | ID of existing location to reference |
| `city` | string | Conditional** | City name |
| `state` | string | Conditional** | State/province name |
| `country` | string | No | Country name |
| `name` | string | No | Location name (defaults to "City, State") |
| `address` | string | No | Full street address |
| `pin_code` | string | No | Postal/ZIP code |
| `lat` | float | No | Latitude coordinate |
| `lng` | float | No | Longitude coordinate |

\* Required if not providing city/state  
\*\* Required if not providing location_id

#### Success Response

**Status Code:** `201 Created`

**Response Body:**
```json
{
  "id": integer,
  "name": string,
  "description": string,
  "created_by_id": integer,
  "tour_operator_id": integer,
  "locations": [
    {
      "id": integer,
      "name": string,
      "city": string,
      "state": string,
      "country": string,
      "pin_code": string,
      "address": string,
      "lng": float,
      "lat": float
    }
  ],
  "image_ids": [integer]
}
```

#### Error Responses

**Status Code:** `400 Bad Request`
```json
{
  "error": "tour_operator_id, user_id, name, locations are required fields."
}
```

**Status Code:** `400 Bad Request`
```json
{
  "error": "Invalid tour operator ID"
}
```

**Status Code:** `400 Bad Request`
```json
{
  "error": "Invalid user ID"
}
```

**Status Code:** `400 Bad Request`
```json
{
  "error": "Invalid location ID"
}
```

**Status Code:** `409 Conflict`
```json
{
  "error": "The destination already exists."
}
```

**Status Code:** `500 Internal Server Error`
```json
{
  "error": "Error message details"
}
```

---

### 2. Get Destinations

Retrieves destinations with their associated location details. Supports pagination.

#### Endpoint
```
POST /destination/get/
```

#### Method Name
`get_destinations(request)`

#### Request Headers
```
Content-Type: application/json
```

#### Request Body

```json
{
  "tour_operator_id": integer (optional),
  "user_id": integer (optional),
  "page": integer (optional)
}
```

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tour_operator_id` | integer | Conditional* | Filter by tour operator ID |
| `user_id` | integer | Conditional* | Filter by specific destination ID |
| `page` | integer | No | Page number for pagination (default: 1) |

\* At least one of `tour_operator_id` or `user_id` is required

#### Success Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "data": [
    {
      "id": integer,
      "name": string,
      "description": string,
      "created_by_id": integer,
      "tour_operator_id": integer,
      "locations": [
        {
          "state": string,
          "city": string,
          "id": integer (if location object exists),
          "name": string (if location object exists),
          "address": string (if location object exists),
          "pin_code": string (if location object exists),
          "country": string (if location object exists),
          "lng": float (if location object exists),
          "lat": float (if location object exists)
        }
      ],
      "image_ids": [integer]
    }
  ],
  "pagination": {
    "count": integer,
    "num_pages": integer,
    "current_page": integer,
    "next": string (URL or null),
    "previous": string (URL or null)
  }
}
```

#### Response Fields

**Destination Object:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Destination ID |
| `name` | string | Destination name |
| `description` | string | Destination description |
| `created_by_id` | integer | ID of user who created |
| `tour_operator_id` | integer | ID of tour operator |
| `locations` | array | Array of location objects |
| `image_ids` | array | Array of image IDs associated with destination |

**Location Object (in response):**

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `state` | string | Yes | State/province name |
| `city` | string | Yes | City name |
| `id` | integer | No* | Location ID |
| `name` | string | No* | Location name |
| `address` | string | No* | Full address |
| `pin_code` | string | No* | Postal code |
| `country` | string | No* | Country name |
| `lng` | float | No* | Longitude |
| `lat` | float | No* | Latitude |

\* These fields are only present if the destination has a linked Location object (new data). Old destinations may only have city/state.

**Pagination Object:**

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Total number of destinations |
| `num_pages` | integer | Total number of pages |
| `current_page` | integer | Current page number |
| `next` | string/null | URL for next page or null |
| `previous` | string/null | URL for previous page or null |

#### Error Responses

**Status Code:** `400 Bad Request`
```json
{
  "status": "failed",
  "code": 400,
  "message": "User_id or tour_operator_id is required"
}
```

---

## Image Management

Destinations support multiple images through a centralized image management system. Images are stored separately in the `ImageMetadata` model and linked to destinations via the `image_ids` field.

### Upload Images

Upload one or more images for a destination.

#### Endpoint
```
POST /image/upload/
```

#### Request Type
`multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tour_operator_id` | integer | Yes | ID of the tour operator |
| `module` | string | Yes | Must be "destination" |
| `record_id` | integer | Yes | ID of the destination |
| `images` | file[] | Yes | Array of image files to upload |
| `description` | string[] | No | Array of descriptions for each image |
| `order` | integer[] | No | Array of display order for each image |

#### Success Response

**Status Code:** `200 OK`

**Response Body:**
```json
[
  {
    "message": "Image uploaded successfully",
    "image_id": integer,
    "file_name": string
  }
]
```

#### Error Responses

**Status Code:** `400 Bad Request`
```json
{
  "error": "Missing required parameters"
}
```

**Status Code:** `400 Bad Request`
```json
{
  "error": "Quota exceeded for image uploads"
}
```

#### Example

```bash
# Using curl
curl -X POST http://your-domain/image/upload/ \
  -F "tour_operator_id=1" \
  -F "module=destination" \
  -F "record_id=42" \
  -F "images=@beach1.jpg" \
  -F "images=@beach2.jpg" \
  -F "description=Beautiful sunset view" \
  -F "description=Beach activities" \
  -F "order=1" \
  -F "order=2"
```

---

### Get Images

Retrieve all images associated with a destination.

#### Endpoint
```
POST /image/get/
```

#### Request Headers
```
Content-Type: application/json
```

#### Request Body

```json
{
  "tour_operator_id": integer,
  "module": string,
  "record_id": integer (optional),
  "include_binary": boolean (optional)
}
```

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tour_operator_id` | integer | Yes | ID of the tour operator |
| `module` | string | Yes | Must be "destination" |
| `record_id` | integer | No | ID of specific destination (if omitted, returns all images for the module) |
| `include_binary` | boolean | No | Whether to include base64 encoded image data (default: false) |

#### Success Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "images": [
    {
      "id": integer,
      "description": string,
      "order": integer,
      "image_url": string,
      "image_binary": string (if include_binary=true)
    }
  ]
}
```

#### Example

**Request:**
```json
POST /image/get/

{
  "tour_operator_id": 1,
  "module": "destination",
  "record_id": 42,
  "include_binary": false
}
```

**Response:**
```json
{
  "images": [
    {
      "id": 101,
      "description": "Beautiful sunset view",
      "order": 1,
      "image_url": "/media/images/2024/01/15/beach1.jpg"
    },
    {
      "id": 102,
      "description": "Beach activities",
      "order": 2,
      "image_url": "/media/images/2024/01/15/beach2.jpg"
    }
  ]
}
```

---

### Delete Images

Delete a specific image from a destination.

#### Endpoint
```
POST /image/delete/
```

#### Request Headers
```
Content-Type: application/json
```

#### Request Body

```json
{
  "image_id": integer
}
```

#### Request Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_id` | integer | Yes | ID of the image to delete |

#### Success Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "message": "Image deleted successfully"
}
```

#### Error Responses

**Status Code:** `400 Bad Request`
```json
{
  "error": "image_id is required"
}
```

**Status Code:** `404 Not Found`
```json
{
  "error": "Image entry not found in the database"
}
```

#### Example

**Request:**
```json
POST /image/delete/

{
  "image_id": 101
}
```

**Response:**
```json
{
  "message": "Image deleted successfully"
}
```

#### Notes

- Deleting an image removes it from both the database and the file system
- The image ID is automatically removed from the destination's `image_ids` array
- Images are compressed to JPEG format with 75% quality during upload
- Image quota limits are enforced per tour operator

---

## Relationship with Location

### Overview

Destinations have a many-to-many relationship with Locations through the `StateCityToDestinationMapping` table. This allows:

1. **Multiple locations per destination**: A destination can span multiple cities/locations
2. **Shared locations**: The same location can be associated with multiple destinations
3. **Backward compatibility**: Old destinations without full location data still work

### Data Flow

```
Destination (1) ←→ (N) StateCityToDestinationMapping (N) ←→ (1) Location
                              ↓
                         StateCity (stores city/state pairs)
```

### How It Works

1. **Creating a Destination:**
   - When you create a destination with locations, the system:
     - Creates or retrieves a `StateCity` record for each city/state pair
     - Creates or retrieves a `Location` object with full details (address, coordinates, etc.)
     - Creates a `StateCityToDestinationMapping` linking the destination to both the StateCity and Location

2. **Retrieving Destinations:**
   - The system fetches all `StateCityToDestinationMapping` records for the destination
   - For each mapping, it returns:
     - City and state (always available)
     - Full location details (if a Location object is linked)

3. **Backward Compatibility:**
   - Old destinations created before the location tracking fix may only have city/state data
   - These destinations will return location objects with only `city` and `state` fields
   - New destinations will have complete location information

### Location Reuse

When creating a destination, you can:

1. **Reference an existing location** by providing `location_id`:
   ```json
   {
     "location_id": 123
   }
   ```

2. **Create a new location** by providing full details:
   ```json
   {
     "city": "Goa",
     "state": "Goa",
     "country": "India",
     "name": "Calangute Beach Area",
     "address": "Calangute, North Goa, Goa 403516",
     "pin_code": "403516",
     "lat": 15.5467,
     "lng": 73.7553
   }
   ```

The system uses `get_or_create` logic to avoid duplicate locations. It matches on:
- `tour_operator`
- `name`
- `city`
- `state`
- `country`

---

## Error Handling

### Common Error Scenarios

1. **Missing Required Fields**
   - Status: 400
   - Occurs when required fields are not provided in the request

2. **Invalid References**
   - Status: 400
   - Occurs when tour_operator_id, user_id, or location_id doesn't exist

3. **Duplicate Destination**
   - Status: 409
   - Occurs when a destination with the same name already exists for the tour operator

4. **Database Errors**
   - Status: 500
   - Occurs when there's an unexpected database or system error

### Transaction Safety

Both `add_destination` uses database transactions (`transaction.atomic()`), ensuring:
- All changes are committed together or rolled back on error
- Data consistency is maintained
- No partial updates occur

---

## Examples

### Example 1: Create Destination with New Locations

**Request:**
```json
POST /destination/add/

{
  "tour_operator_id": 1,
  "user_id": 5,
  "name": "Goa Beach Paradise",
  "description": "Experience the best beaches and nightlife in Goa",
  "locations": [
    {
      "city": "Goa",
      "state": "Goa",
      "country": "India",
      "name": "Calangute Beach Area",
      "address": "Calangute, North Goa, Goa 403516",
      "pin_code": "403516",
      "lat": 15.5467,
      "lng": 73.7553
    },
    {
      "city": "Goa",
      "state": "Goa",
      "country": "India",
      "name": "Baga Beach Area",
      "address": "Baga, North Goa, Goa 403516",
      "pin_code": "403516",
      "lat": 15.5556,
      "lng": 73.7515
    }
  ]
}
```

**Response:**
```json
{
  "id": 42,
  "name": "Goa Beach Paradise",
  "description": "Experience the best beaches and nightlife in Goa",
  "created_by_id": 5,
  "tour_operator_id": 1,
  "locations": [
    {
      "id": 101,
      "name": "Calangute Beach Area",
      "city": "Goa",
      "state": "Goa",
      "country": "India",
      "pin_code": "403516",
      "address": "Calangute, North Goa, Goa 403516",
      "lng": 73.7553,
      "lat": 15.5467
    },
    {
      "id": 102,
      "name": "Baga Beach Area",
      "city": "Goa",
      "state": "Goa",
      "country": "India",
      "pin_code": "403516",
      "address": "Baga, North Goa, Goa 403516",
      "lng": 73.7515,
      "lat": 15.5556
    }
  ],
  "image_ids": []
}
```

### Example 2: Create Destination with Existing Location Reference

**Request:**
```json
POST /destination/add/

{
  "tour_operator_id": 1,
  "user_id": 5,
  "name": "Kerala Backwaters Tour",
  "description": "Explore the serene backwaters of Kerala",
  "locations": [
    {
      "location_id": 101
    }
  ]
}
```

**Response:**
```json
{
  "id": 43,
  "name": "Kerala Backwaters Tour",
  "description": "Explore the serene backwaters of Kerala",
  "created_by_id": 5,
  "tour_operator_id": 1,
  "locations": [
    {
      "id": 101,
      "name": "Alleppey Backwaters",
      "city": "Alappuzha",
      "state": "Kerala",
      "country": "India",
      "pin_code": "688001",
      "address": "Alleppey, Kerala 688001",
      "lng": 76.3388,
      "lat": 9.4981
    }
  ],
  "image_ids": []
}
```

### Example 3: Create Destination with Mixed Location Types

**Request:**
```json
POST /destination/add/

{
  "tour_operator_id": 1,
  "user_id": 5,
  "name": "Rajasthan Heritage Tour",
  "description": "Discover the royal heritage of Rajasthan",
  "locations": [
    {
      "location_id": 205
    },
    {
      "city": "Udaipur",
      "state": "Rajasthan",
      "country": "India",
      "name": "City Palace Area",
      "address": "City Palace Road, Udaipur, Rajasthan 313001",
      "pin_code": "313001",
      "lat": 24.5761,
      "lng": 73.6833
    }
  ]
}
```

**Response:**
```json
{
  "id": 44,
  "name": "Rajasthan Heritage Tour",
  "description": "Discover the royal heritage of Rajasthan",
  "created_by_id": 5,
  "tour_operator_id": 1,
  "locations": [
    {
      "id": 205,
      "name": "Jaipur City Center",
      "city": "Jaipur",
      "state": "Rajasthan",
      "country": "India",
      "pin_code": "302001",
      "address": "Jaipur, Rajasthan 302001",
      "lng": 75.7873,
      "lat": 26.9124
    },
    {
      "id": 206,
      "name": "City Palace Area",
      "city": "Udaipur",
      "state": "Rajasthan",
      "country": "India",
      "pin_code": "313001",
      "address": "City Palace Road, Udaipur, Rajasthan 313001",
      "lng": 73.6833,
      "lat": 24.5761
    }
  ],
  "image_ids": []
}
```

### Example 4: Get All Destinations for Tour Operator

**Request:**
```json
POST /destination/get/

{
  "tour_operator_id": 1,
  "page": 1
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 42,
      "name": "Goa Beach Paradise",
      "description": "Experience the best beaches and nightlife in Goa",
      "created_by_id": 5,
      "tour_operator_id": 1,
      "locations": [
        {
          "state": "Goa",
          "city": "Goa",
          "id": 101,
          "name": "Calangute Beach Area",
          "address": "Calangute, North Goa, Goa 403516",
          "pin_code": "403516",
          "country": "India",
          "lng": 73.7553,
          "lat": 15.5467
        },
        {
          "state": "Goa",
          "city": "Goa",
          "id": 102,
          "name": "Baga Beach Area",
          "address": "Baga, North Goa, Goa 403516",
          "pin_code": "403516",
          "country": "India",
          "lng": 73.7515,
          "lat": 15.5556
        }
      ],
      "image_ids": [201, 202, 203]
    },
    {
      "id": 43,
      "name": "Kerala Backwaters Tour",
      "description": "Explore the serene backwaters of Kerala",
      "created_by_id": 5,
      "tour_operator_id": 1,
      "locations": [
        {
          "state": "Kerala",
          "city": "Alappuzha",
          "id": 101,
          "name": "Alleppey Backwaters",
          "address": "Alleppey, Kerala 688001",
          "pin_code": "688001",
          "country": "India",
          "lng": 76.3388,
          "lat": 9.4981
        }
      ],
      "image_ids": [204]
    }
  ],
  "pagination": {
    "count": 15,
    "num_pages": 2,
    "current_page": 1,
    "next": "/destination/get/?page=2",
    "previous": null
  }
}
```

### Example 5: Get Specific Destination by ID

**Request:**
```json
POST /destination/get/

{
  "user_id": 42
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 42,
      "name": "Goa Beach Paradise",
      "description": "Experience the best beaches and nightlife in Goa",
      "created_by_id": 5,
      "tour_operator_id": 1,
      "locations": [
        {
          "state": "Goa",
          "city": "Goa",
          "id": 101,
          "name": "Calangute Beach Area",
          "address": "Calangute, North Goa, Goa 403516",
          "pin_code": "403516",
          "country": "India",
          "lng": 73.7553,
          "lat": 15.5467
        },
        {
          "state": "Goa",
          "city": "Goa",
          "id": 102,
          "name": "Baga Beach Area",
          "address": "Baga, North Goa, Goa 403516",
          "pin_code": "403516",
          "country": "India",
          "lng": 73.7515,
          "lat": 15.5556
        }
      ],
      "image_ids": [201, 202, 203]
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

### Example 6: Backward Compatibility - Old Destination

**Response for old destination (created before location tracking fix):**
```json
{
  "data": [
    {
      "id": 10,
      "name": "Old Destination",
      "description": "Created before the location tracking update",
      "created_by_id": 3,
      "tour_operator_id": 1,
      "locations": [
        {
          "state": "Maharashtra",
          "city": "Mumbai"
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

**Note:** Old destinations only have `city` and `state` fields. They don't have `id`, `name`, `address`, `coordinates`, etc.

### Example 7: Complete Workflow with Images

This example shows the complete workflow of creating a destination and managing its images.

**Step 1: Create Destination**
```json
POST /destination/add/

{
  "tour_operator_id": 1,
  "user_id": 5,
  "name": "Manali Adventure Package",
  "description": "Experience adventure sports in the Himalayas",
  "locations": [
    {
      "city": "Manali",
      "state": "Himachal Pradesh",
      "country": "India",
      "name": "Solang Valley",
      "address": "Solang Valley, Manali, Himachal Pradesh 175103",
      "pin_code": "175103",
      "lat": 32.3199,
      "lng": 77.1497
    }
  ]
}
```

**Response:**
```json
{
  "id": 50,
  "name": "Manali Adventure Package",
  "description": "Experience adventure sports in the Himalayas",
  "created_by_id": 5,
  "tour_operator_id": 1,
  "locations": [
    {
      "id": 250,
      "name": "Solang Valley",
      "city": "Manali",
      "state": "Himachal Pradesh",
      "country": "India",
      "pin_code": "175103",
      "address": "Solang Valley, Manali, Himachal Pradesh 175103",
      "lng": 77.1497,
      "lat": 32.3199
    }
  ],
  "image_ids": []
}
```

**Step 2: Upload Images**
```bash
curl -X POST http://your-domain/image/upload/ \
  -F "tour_operator_id=1" \
  -F "module=destination" \
  -F "record_id=50" \
  -F "images=@manali_mountains.jpg" \
  -F "images=@paragliding.jpg" \
  -F "images=@snow_activities.jpg" \
  -F "description=Himalayan mountain view" \
  -F "description=Paragliding adventure" \
  -F "description=Snow activities" \
  -F "order=1" \
  -F "order=2" \
  -F "order=3"
```

**Response:**
```json
[
  {
    "message": "Image uploaded successfully",
    "image_id": 301,
    "file_name": "manali_mountains.jpg"
  },
  {
    "message": "Image uploaded successfully",
    "image_id": 302,
    "file_name": "paragliding.jpg"
  },
  {
    "message": "Image uploaded successfully",
    "image_id": 303,
    "file_name": "snow_activities.jpg"
  }
]
```

**Step 3: Get Destination with Images**
```json
POST /destination/get/

{
  "user_id": 50
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 50,
      "name": "Manali Adventure Package",
      "description": "Experience adventure sports in the Himalayas",
      "created_by_id": 5,
      "tour_operator_id": 1,
      "locations": [
        {
          "state": "Himachal Pradesh",
          "city": "Manali",
          "id": 250,
          "name": "Solang Valley",
          "address": "Solang Valley, Manali, Himachal Pradesh 175103",
          "pin_code": "175103",
          "country": "India",
          "lng": 77.1497,
          "lat": 32.3199
        }
      ],
      "image_ids": [301, 302, 303]
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

**Step 4: Get Image Details**
```json
POST /image/get/

{
  "tour_operator_id": 1,
  "module": "destination",
  "record_id": 50,
  "include_binary": false
}
```

**Response:**
```json
{
  "images": [
    {
      "id": 301,
      "description": "Himalayan mountain view",
      "order": 1,
      "image_url": "/media/images/2024/01/15/manali_mountains.jpg"
    },
    {
      "id": 302,
      "description": "Paragliding adventure",
      "order": 2,
      "image_url": "/media/images/2024/01/15/paragliding.jpg"
    },
    {
      "id": 303,
      "description": "Snow activities",
      "order": 3,
      "image_url": "/media/images/2024/01/15/snow_activities.jpg"
    }
  ]
}
```

---

## Integration with Car Dealer API

Destinations are used to filter car dealers by location. See the Car Dealer API documentation for details on filtering car dealers by destination.

**Example:**
```json
POST /cardealer/get/

{
  "tour_operator_id": 1,
  "destination_id": 42
}
```

This will return only car dealers whose locations match the locations associated with destination ID 42.

---

## Best Practices

### 1. Location Reuse
- Before creating a new location, check if a similar location already exists
- Use `location_id` to reference existing locations when possible
- This prevents duplicate location records and maintains data consistency

### 2. Complete Location Data
- Always provide complete location information (address, coordinates, pin code)
- Coordinates (lat/lng) are especially important for mapping and distance calculations
- Use consistent naming conventions for locations

### 3. Destination Naming
- Use descriptive, unique names for destinations
- Include the region or theme in the name (e.g., "Goa Beach Paradise" instead of just "Goa")
- Avoid duplicate destination names within the same tour operator

### 4. Error Handling
- Always check for error responses and handle them appropriately
- Use the transaction safety to ensure data consistency
- Validate input data before sending requests

### 5. Pagination
- Use pagination when retrieving large numbers of destinations
- Default page size is 10 items
- Always check the `pagination` object for navigation

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│   Destination   │
├─────────────────┤
│ id (PK)         │
│ tour_operator_id│
│ created_by      │
│ name            │
│ description     │
│ created_at      │
│ image_ids       │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌──────────────────────────────┐
│StateCityToDestinationMapping │
├──────────────────────────────┤
│ id (PK)                      │
│ state_city_id (FK)           │
│ destination_id (FK)          │
│ location_id (FK, nullable)   │
└────┬─────────────────┬───────┘
     │                 │
     │ N:1             │ N:1
     │                 │
     ▼                 ▼
┌────────────┐   ┌──────────┐
│ StateCity  │   │ Location │
├────────────┤   ├──────────┤
│ id (PK)    │   │ id (PK)  │
│ state      │   │ name     │
│ city       │   │ city     │
└────────────┘   │ state    │
                 │ country  │
                 │ address  │
                 │ pin_code │
                 │ lat      │
                 │ lng      │
                 │ ...      │
                 └──────────┘
```

---

## Version History

### Version 2.0 (Current)
- Added full Location object tracking
- Support for both location_id reference and new location creation
- Enhanced location details in responses (address, coordinates, pin code)
- Backward compatibility with old destinations
- Transaction safety for data consistency

### Version 1.0 (Legacy)
- Basic destination management
- Only city/state tracking (no full location objects)
- No coordinate or address support

---

## Support

For issues or questions regarding the Destination API:
1. Check the error response for specific error messages
2. Verify all required fields are provided
3. Ensure referenced IDs (tour_operator_id, user_id, location_id) exist
4. Check database migration status if location fields are missing

---

## Related APIs

- **Location API**: Manage standalone locations
- **Car Dealer API**: Filter car dealers by destination
- **Package API**: Create tour packages for destinations
- **Hotel API**: Associate hotels with destination locations
- **Event API**: Link events to destination locations

