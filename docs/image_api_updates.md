# Image API Updates

## Overview

We've updated the image handling in the API to make it easier to work with images for hotels, rooms, and other entities. The main changes are:

1. Each entity (Hotel, Room, Package, etc.) now has an `image_ids` field that stores a list of image IDs.
2. When you upload an image, the image ID is automatically added to the `image_ids` field of the corresponding entity.
3. When you delete an image, the image ID is automatically removed from the `image_ids` field of the corresponding entity.
4. The API now returns images for each entity based on the `image_ids` field.

## API Endpoints

The image API endpoints remain the same:

- `POST /image/upload/` - Upload one or more images
- `POST /image/get/` - Get images for a specific module and record ID
- `POST /image/delete/` - Delete an image

## Image Upload

When uploading images, you need to provide:

- `tour_operator_id` - The ID of the tour operator
- `module` - The module name (e.g., 'hotel', 'room', 'package', etc.)
- `record_id` - The ID of the record to associate the image with
- `images` - The image files to upload
- `description` (optional) - Description for each image
- `order` (optional) - Order for each image

Example:

```
POST /image/upload/
{
  "tour_operator_id": 1,
  "module": "hotel",
  "record_id": 123,
  "images": [file1, file2],
  "description": ["Hotel front view", "Hotel lobby"],
  "order": [1, 2]
}
```

## Image Retrieval

When retrieving images, you need to provide:

- `tour_operator_id` - The ID of the tour operator
- `module` - The module name (e.g., 'hotel', 'room', 'package', etc.)
- `record_id` (optional) - The ID of the record to get images for
- `include_binary` (optional) - Whether to include the binary data of the images (default: false)

Example:

```
POST /image/get/
{
  "tour_operator_id": 1,
  "module": "hotel",
  "record_id": 123,
  "include_binary": true
}
```

Response:

```json
{
  "images": [
    {
      "id": 1,
      "description": "Hotel front view",
      "order": 1,
      "image_url": "/media/images/2025/04/16/hotel_front.jpg",
      "image_binary": "base64-encoded-binary-data"
    },
    {
      "id": 2,
      "description": "Hotel lobby",
      "order": 2,
      "image_url": "/media/images/2025/04/16/hotel_lobby.jpg",
      "image_binary": "base64-encoded-binary-data"
    }
  ]
}
```

Note: The `image_binary` field contains the base64-encoded binary data of the image. You can use this to display the image directly in your application without making a separate request to the `image_url`. For example, in HTML you can use it like this:

```html
<img src="data:image/jpeg;base64,image_binary_data_here" alt="Image description" />
```

Or in React:

```jsx
<img src={`data:image/jpeg;base64,${image.image_binary}`} alt={image.description} />
```

The `include_binary` parameter is also available in the following API endpoints:

- `POST /hotel/get/` - Get hotels
- `POST /hotel/get_rooms/` - Get rooms

Example:

```
POST /hotel/get/
{
  "tour_operator_id": 1,
  "include_binary": true
}
```

## Image Deletion

When deleting an image, you need to provide:

- `image_id` - The ID of the image to delete

Example:

```
POST /image/delete/
{
  "image_id": 1
}
```

Response:

```json
{
  "message": "Image deleted successfully"
}
```

## Entity API Changes

The API endpoints for entities (Hotel, Room, Package, etc.) now include the `image_ids` field in the response. This field contains a list of image IDs associated with the entity.

For example, when retrieving a hotel:

```json
{
  "id": 123,
  "name": "Grand Hotel",
  "description": "A luxury hotel",
  "ratings": 4.5,
  "website": "https://grandhotel.com",
  "phoneno": "123-456-7890",
  "location": {
    "id": 456,
    "name": "Downtown",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "lat": 40.7128,
    "lng": -74.0060
  },
  "amenities": [...],
  "inclusions": [...],
  "exclusions": [...],
  "policies": [...],
  "images": [
    {
      "id": 1,
      "description": "Hotel front view",
      "order": 1,
      "image_url": "/media/images/2025/04/16/hotel_front.jpg"
    },
    {
      "id": 2,
      "description": "Hotel lobby",
      "order": 2,
      "image_url": "/media/images/2025/04/16/hotel_lobby.jpg"
    }
  ],
  "rooms": [...]
}
```

## Implementation Details

- The `image_ids` field is a JSON field that stores a list of image IDs.
- When you upload an image, the image ID is automatically added to the `image_ids` field of the corresponding entity.
- When you delete an image, the image ID is automatically removed from the `image_ids` field of the corresponding entity.
- The API now returns images for each entity based on the `image_ids` field.
- If an entity doesn't have an `image_ids` field or it's empty, the API falls back to the old method of retrieving images based on the module and record ID.

## Benefits

- Faster image retrieval: Images are retrieved directly using their IDs instead of querying by module and record ID.
- Better data integrity: The relationship between entities and images is stored in the entity itself, making it easier to maintain.
- Easier to work with: The API now returns images for each entity in a more consistent way.
