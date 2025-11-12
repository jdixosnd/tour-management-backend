# Itinerary Item Image Upload - UI Implementation Guide

## Overview
Itinerary items now support image uploads using the **same endpoints** as other modules (hotels, rooms, packages, events, sightseeing). No new endpoints were created - just use the existing image endpoints with `module='itinerary_item'`.

---

## 1. Upload Images

### Endpoint
```
POST /image/upload/
```

### Request Format
`multipart/form-data`

### Required Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `tour_operator_id` | number | Tour operator ID | `1` |
| `module` | string | Module type | `"itinerary_item"` |
| `record_id` | number | Itinerary item ID | `123` |
| `images` | file(s) | Image file(s) to upload | Multiple files supported |

### Optional Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `description[]` | string[] | Description for each image | `["First image", "Second image"]` |
| `order[]` | number[] | Order/sequence for each image | `[0, 1]` |


---

## 2. Get Images

### Endpoint
```
GET /image/get/?module=itinerary_item&record_id=123
```

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `module` | string | Yes | Module type | `itinerary_item` |
| `record_id` | number | Yes | Itinerary item ID | `123` |
| `include_binary` | boolean | No | Include base64 image data | `false` (default) |


**Note**: Images are returned sorted by the `order` field.

---

## 3. Delete Image

### Endpoint
```
POST /image/delete/
```

### Request Format
`application/json`

### Required Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `image_id` | number | ID of the image to delete | `456` |


## Important Notes

### Image Quota
- **Maximum 5 images** per itinerary item (default quota)
- Backend enforces this limit
- Attempting to upload more will return an error

### Image Processing
- Images are automatically compressed to JPEG format with 75% quality
- Original filename is preserved in the response

### Module Values
The same endpoints work for all modules. Just change the `module` parameter:
- `"itinerary_item"` - For itinerary items
- `"hotel"` - For hotels
- `"room"` - For rooms
- `"package"` - For packages
- `"event"` - For events
- `"sightseeing"` - For sightseeing
- `"destination"` - For destinations
- `"car_dealer"` - For car dealers

### Image URLs
To display images in the UI, construct the URL using the `image_path` from the response:
```javascript
const imageUrl = `${BASE_URL}/media/${image.image_path}`;
```

---

