# Activity Image Support - Integration Guide

## Overview

Image support has been added to package activities (Event and SightSeeing). This document describes the affected APIs and how to integrate image support for packages.

## Affected APIs

### 1. Package Retrieval API (Modified)

**Endpoint:** `POST /package/get/`

**What Changed:**
- Activities in the response now include two new fields:
  - `image_ids`: Array of image IDs associated with the activity
  - `images`: Array of image objects with full metadata

**Request:** (No changes)
```json
{
  "tour_operator_id": 1,
  "package_id": 123
}
```

**Response:** (New fields added)
```json
{
  "data": [
    {
      "id": 123,
      "name": "Manali Adventure Package",
      "itinerary_details": [
        {
          "day": 1,
          "activities": [
            {
              "name": "River Rafting",
              "type": "event",
              "description": "Exciting rafting experience",
              "charges": 1500.00,
              "contact_no": "+91-9876543210",
              "sequence": 1,
              "location": {...},
              "image_ids": [101, 102],
              "images": [
                {
                  "id": 101,
                  "description": "Rafting action shot",
                  "order": 1,
                  "image_url": "/media/images/2025/11/10/rafting_1.jpg"
                },
                {
                  "id": 102,
                  "description": "Safety briefing",
                  "order": 2,
                  "image_url": "/media/images/2025/11/10/rafting_2.jpg"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## How to Integrate Image Support

### 1. Upload Images to Activities

Use the existing Image Upload API to add images to activities (events or sightseeing).

**Endpoint:** `POST /image/upload/`

**Request:**
```bash
curl -X POST http://localhost:8000/image/upload/ \
  -F "tour_operator_id=1" \
  -F "module=event" \
  -F "record_id=123" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "description=Activity photo 1" \
  -F "description=Activity photo 2" \
  -F "order=1" \
  -F "order=2"
```

**Parameters:**
- `tour_operator_id`: Tour operator ID (required)
- `module`: Either `"event"` or `"sightseeing"` (required)
- `record_id`: The activity ID (required)
- `images`: Image file(s) to upload (required, can be multiple)
- `description`: Description for each image (optional)
- `order`: Display order for each image (optional)

**Response:**
```json
{
  "message": "Images uploaded successfully",
  "image_ids": [101, 102]
}
```

### 2. Retrieve Package with Activity Images

Images are automatically included when you retrieve package details.

**Endpoint:** `POST /package/get/`

**Request:**
```json
{
  "tour_operator_id": 1,
  "package_id": 123
}
```

**Response includes images in activities:**
```json
{
  "data": [
    {
      "itinerary_details": [
        {
          "activities": [
            {
              "name": "River Rafting",
              "type": "event",
              "image_ids": [101, 102],
              "images": [
                {
                  "id": 101,
                  "description": "Activity photo 1",
                  "order": 1,
                  "image_url": "/media/images/2025/11/10/image1.jpg"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 3. Get Images for Specific Activity (Optional)

If you need to retrieve images for a specific activity separately.

**Endpoint:** `POST /image/get/`

**Request:**
```json
{
  "tour_operator_id": 1,
  "module": "event",
  "record_id": 123,
  "include_binary": false
}
```

**Response:**
```json
{
  "images": [
    {
      "id": 101,
      "description": "Activity photo 1",
      "order": 1,
      "image_url": "/media/images/2025/11/10/image1.jpg"
    },
    {
      "id": 102,
      "description": "Activity photo 2",
      "order": 2,
      "image_url": "/media/images/2025/11/10/image2.jpg"
    }
  ]
}
```

### 4. Delete Activity Images

**Endpoint:** `POST /image/delete/`

**Request:**
```json
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

## Integration Workflow

### Complete Example: Adding Images to Package Activities

**Step 1:** Create a package with activities (existing functionality)

**Step 2:** Upload images for each activity
```bash
# Upload images for Event activity (ID: 45)
POST /image/upload/
{
  "tour_operator_id": 1,
  "module": "event",
  "record_id": 45,
  "images": [file1.jpg, file2.jpg]
}

# Upload images for SightSeeing activity (ID: 78)
POST /image/upload/
{
  "tour_operator_id": 1,
  "module": "sightseeing",
  "record_id": 78,
  "images": [file3.jpg]
}
```

**Step 3:** Retrieve package - images are automatically included
```bash
POST /package/get/
{
  "tour_operator_id": 1,
  "package_id": 123
}
```

**Step 4:** Display images in your frontend
```javascript
// Example: React/JavaScript
activities.forEach(activity => {
  activity.images.forEach(image => {
    const imageUrl = `${BASE_URL}${image.image_url}`;
    // Display image using imageUrl
  });
});
```

## Important Notes

### Module Names
- Use `"event"` for Event activities
- Use `"sightseeing"` for SightSeeing activities
- Module names are case-sensitive (use lowercase)

### Backward Compatibility
- Activities without images will have empty arrays: `"image_ids": []` and `"images": []`
- No breaking changes to existing API responses
- Existing integrations will continue to work

### Image URL Format
- Image URLs are relative: `/media/images/2025/11/10/filename.jpg`
- Prepend your base URL: `https://yourdomain.com/media/images/...`
- For base64 data, set `"include_binary": true` in the image get request

### Supported Image Formats
- JPEG, PNG, GIF, WebP
- Maximum file size: 10MB (configurable)

