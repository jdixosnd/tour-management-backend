# Package Image Support Documentation

## Overview

Tour packages now support image uploads. You can upload multiple images for each package, which will be returned in the GET package APIs.

## Features

- Upload multiple images per package
- Images are compressed automatically (JPEG, 75% quality)
- Images are ordered and can have descriptions
- Quota limits per tour operator
- Images are returned in all package GET APIs

---

## API Endpoints

### 1. Upload Package Images

Upload one or more images for a package.

#### Endpoint
```
POST /image/upload/
```

#### Request Type
`multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tour_operator_id` | integer | Yes | Tour operator ID |
| `module` | string | Yes | Must be "package" |
| `record_id` | integer | Yes | Package ID |
| `images` | file[] | Yes | Array of image files |
| `description` | string[] | No | Description for each image |
| `order` | integer[] | No | Display order for each image |

#### Example Request (cURL)

```bash
curl -X POST http://localhost:8000/image/upload/ \
  -F "tour_operator_id=1" \
  -F "module=package" \
  -F "record_id=14" \
  -F "images=@package_cover.jpg" \
  -F "images=@package_detail1.jpg" \
  -F "images=@package_detail2.jpg" \
  -F "description=Package cover image" \
  -F "description=Destination view" \
  -F "description=Hotel accommodation" \
  -F "order=1" \
  -F "order=2" \
  -F "order=3"
```

#### Example Request (JavaScript/Fetch)

```javascript
const formData = new FormData();
formData.append('tour_operator_id', '1');
formData.append('module', 'package');
formData.append('record_id', '14');
formData.append('images', file1); // File object from input
formData.append('images', file2);
formData.append('images', file3);
formData.append('description', 'Package cover image');
formData.append('description', 'Destination view');
formData.append('description', 'Hotel accommodation');
formData.append('order', '1');
formData.append('order', '2');
formData.append('order', '3');

fetch('http://localhost:8000/image/upload/', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Success Response

**Status Code:** `201 Created`

```json
{
  "results": [
    {
      "message": "Image uploaded successfully",
      "image_id": 101,
      "file_name": "package_cover.jpg"
    },
    {
      "message": "Image uploaded successfully",
      "image_id": 102,
      "file_name": "package_detail1.jpg"
    },
    {
      "message": "Image uploaded successfully",
      "image_id": 103,
      "file_name": "package_detail2.jpg"
    }
  ]
}
```

#### Error Responses

**Status Code:** `400 Bad Request`
```json
{
  "error": "Missing required parameters"
}
```

**Status Code:** `400 Bad Request` (Quota Exceeded)
```json
{
  "error": "Quota exceeded for image uploads"
}
```

---

### 2. Get Package with Images

Retrieve package details including images.

#### Endpoint
```
POST /package/get/
```

#### Request Body

```json
{
  "tour_operator_id": 1,
  "package_id": 14
}
```

#### Success Response

**Status Code:** `200 OK`

```json
{
  "data": [
    {
      "id": 14,
      "name": "Malaysia Adventure Package",
      "destination_id": 2,
      "description": "Explore the beauty of Malaysia",
      "pax_size": 2,
      "contains_travel_fare": 1,
      "transport_type": "FLIGHT",
      "no_of_days": 5,
      "package_amount": 11111.0,
      "is_active": true,
      "type": "Adventure",
      "terms_and_conditions": "<div>...</div>",
      "itinerary_details": [...],
      "inclusions": [...],
      "exclusions": [...],
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
          "image_url": "/media/images/2024/01/15/package_detail1.jpg"
        },
        {
          "id": 103,
          "description": "Hotel accommodation",
          "order": 3,
          "image_url": "/media/images/2024/01/15/package_detail2.jpg"
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

---

### 3. Get Packages from Destination (with Images)

Retrieve all packages for a destination including images.

#### Endpoint
```
POST /package/get_packages_from_destination/
```

#### Request Body

```json
{
  "tour_operator_id": 1,
  "destination_id": 2
}
```

#### Success Response

**Status Code:** `200 OK`

```json
{
  "data": [
    {
      "id": 14,
      "name": "Malaysia Adventure Package",
      "destination_id": 2,
      "description": "Explore the beauty of Malaysia",
      "pax_size": 2,
      "contains_travel_fare": 1,
      "transport_type": "FLIGHT",
      "no_of_days": 5,
      "package_amount": 11111.0,
      "is_active": true,
      "type": "Adventure",
      "terms_and_conditions": "<div>...</div>",
      "images": [
        {
          "id": 101,
          "description": "Package cover image",
          "order": 1,
          "image_url": "/media/images/2024/01/15/package_cover.jpg"
        }
      ]
    }
  ],
  "pagination": {...}
}
```

---

### 4. Delete Package Image

Delete a specific image from a package.

#### Endpoint
```
POST /image/delete/
```

#### Request Body

```json
{
  "tour_operator_id": 1,
  "image_id": 101
}
```

#### Success Response

**Status Code:** `200 OK`

```json
{
  "message": "Image deleted successfully"
}
```

---

## Update Package Request Body (with Images)

When updating a package, the images are managed separately through the image upload/delete APIs. The update package API does not directly handle image uploads.

### Sample Update Request

```json
{
  "id": 14,
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Malaysia Adventure Package",
  "destination_id": 2,
  "description": "Explore the beauty of Malaysia",
  "pax_size": 2,
  "contains_travel_fare": 1,
  "transport_type": "FLIGHT",
  "no_of_days": 5,
  "package_amount": 11111.0,
  "is_active": true,
  "type": "Adventure",
  "terms_and_conditions": "<div>...</div>",
  "itinerary_items": [...],
  "inclusions": [...],
  "exclusions": [...]
}
```

**Note:** To add/remove images, use the separate image upload/delete endpoints.

---

## Workflow Example

### Creating a Package with Images

1. **Create the package** using `POST /package/add/`
2. **Get the package ID** from the response
3. **Upload images** using `POST /image/upload/` with the package ID
4. **Retrieve the package** using `POST /package/get/` to see the images

### Updating Package Images

1. **Upload new images** using `POST /image/upload/`
2. **Delete old images** (if needed) using `POST /image/delete/`
3. **Retrieve the package** to verify changes

---

## Image Quota

Each tour operator has a quota for the maximum number of images per package. This is configured in the `TourOperatorQuota` model with the field `max_images_package`.

Default quota: **5 images per package**

If you exceed the quota, you'll receive an error:
```json
{
  "error": "Quota exceeded for image uploads"
}
```

---

## Notes

- Images are automatically compressed to JPEG format at 75% quality
- Images are stored in `/media/images/YYYY/MM/DD/` directory structure
- Images are ordered by the `order` field (ascending)
- The `image_url` field contains the relative path to access the image
- Images are associated with packages using the `image_ids` JSON field in the Package model

