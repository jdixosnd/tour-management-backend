# Frontend Integration Guide - Package API Changes

## Overview

We've made important updates to the Package APIs that affect frontend integration:

1. **Package Images Support** - Packages now return image data

---

## 🔄 What Changed?

### 1. Package GET APIs Now Return Images

**Affected Endpoints:**
- `POST /package/get/` - Get package details
- `POST /package/get_packages_from_destination/` - Get packages by destination

**What's New:**
Both endpoints now include an `images` array in the response containing all package images.

**Before:**
```json
{
  "data": [{
    "id": 14,
    "name": "Malaysia Package",
    "description": "...",
    "inclusions": [...],
    "exclusions": [...]
  }]
}
```

**After:**
```json
{
  "data": [{
    "id": 14,
    "name": "Malaysia Package",
    "description": "...",
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
        "image_url": "/media/images/2024/01/15/destination.jpg"
      }
    ]
  }]
}
```
---

## 📋 Frontend Integration Tasks

### Task 1: Display Package Images

**Where:** Package listing page, package detail page

**Implementation:**

```javascript
// Fetch package data
const response = await fetch('/package/get/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tour_operator_id: 1,
    package_id: 14
  })
});

const data = await response.json();
const packageData = data.data[0];

// Display images
if (packageData.images && packageData.images.length > 0) {
  packageData.images.forEach(image => {
    // Create image element
    const img = document.createElement('img');
    img.src = image.image_url;
    img.alt = image.description || 'Package image';
    
    // Images are ordered by the 'order' field
    // You can use this for carousel/gallery ordering
  });
}
```

**UI Recommendations:**
- Show first image as package cover/thumbnail in listing
- Display all images in a carousel/gallery on detail page
- Images are already sorted by `order` field
- Use `description` field for image alt text or captions

### Task 2: Upload Package Images

**Where:** Package creation/edit form

**Implementation:**

```javascript
// After creating/updating a package, upload images
async function uploadPackageImages(packageId, tourOperatorId, imageFiles) {
  const formData = new FormData();
  
  formData.append('tour_operator_id', tourOperatorId);
  formData.append('module', 'package');
  formData.append('record_id', packageId);
  
  // Add multiple images
  imageFiles.forEach((file, index) => {
    formData.append('images', file);
    formData.append('description', `Package image ${index + 1}`);
    formData.append('order', index + 1);
  });
  
  const response = await fetch('/image/upload/', {
    method: 'POST',
    body: formData // Don't set Content-Type header, browser will set it
  });
  
  return await response.json();
}

// Usage example
const imageInput = document.getElementById('package-images');
const files = Array.from(imageInput.files);

uploadPackageImages(14, 1, files)
  .then(result => {
    console.log('Images uploaded:', result.results);
    // Refresh package data to show new images
  });
```

### Task 3: Delete Package Images

**Where:** Package edit form (image management)

**Implementation:**

```javascript
async function deletePackageImage(tourOperatorId, imageId) {
  const response = await fetch('/image/delete/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tour_operator_id: tourOperatorId,
      image_id: imageId
    })
  });
  
  return await response.json();
}

// Usage example
deletePackageImage(1, 101)
  .then(() => {
    console.log('Image deleted');
    // Refresh package data
  });
```



## ⚠️ Important Notes

### Image Upload Workflow

**Correct Order:**
1. Create/Update package → Get package ID
2. Upload images using package ID
3. Fetch package again to display images

**Don't:**
- Try to upload images in the same request as package create/update
- Images are managed separately via `/image/upload/` endpoint

### Image Quota

- Each tour operator has a quota (default: 5 images per package)
- Handle quota exceeded error gracefully:

```javascript
const result = await uploadPackageImages(packageId, tourOperatorId, files);

result.results.forEach(item => {
  if (item.error) {
    // Show error message to user
    alert(item.error); // "Quota exceeded. Only X images can be uploaded."
  } else {
    // Image uploaded successfully
    console.log('Uploaded:', item.file_name);
  }
});
```

### Backward Compatibility

- **No breaking changes** - existing code will continue to work
- `images` array will be empty `[]` if no images uploaded
- Car dealer `id` is a new field, won't break existing code

### Data Transformation

When using GET response for UPDATE request, remember to transform:

| GET Response Field | UPDATE Request Field |
|-------------------|---------------------|
| `itinerary_details` | `itinerary_items` |
| `hotel_details` (objects) | `hotel_details` (IDs array) |
| `car_dealers` (objects) | `car_dealers` (IDs array) |
| `images` (array) | ❌ Not included in update |

---

## 🧪 Testing Checklist

- [ ] Package listing shows first image as thumbnail
- [ ] Package detail shows all images in gallery
- [ ] Image upload works with multiple files
- [ ] Image delete removes image and refreshes display
- [ ] Quota exceeded error is handled gracefully
- [ ] Packages without images show placeholder
- [ ] Car dealer selection works in edit form
- [ ] Update package preserves car dealer selections

---

## 📞 Support

If you encounter any issues during integration:

1. Check the detailed API documentation:
   - `docs/package_image_support.md` - Complete image API guide
   - `docs/package_api_sample_request_response.md` - Request/response samples

2. Common issues:
   - **Images not showing**: Check `image_url` path and MEDIA_URL configuration
   - **Upload fails**: Verify `multipart/form-data` is used (not JSON)
   - **Quota error**: Check tour operator quota settings

3. Example responses are available in the documentation files for reference

---

## 🚀 Quick Start Example

Complete example for package detail page with images:

```javascript
async function loadPackageDetail(packageId) {
  // Fetch package data
  const response = await fetch('/package/get/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tour_operator_id: 1,
      package_id: packageId
    })
  });
  
  const data = await response.json();
  const pkg = data.data[0];
  
  // Display package info
  document.getElementById('package-name').textContent = pkg.name;
  document.getElementById('package-description').textContent = pkg.description;
  document.getElementById('package-price').textContent = `$${pkg.package_amount}`;
  
  // Display images
  const imageGallery = document.getElementById('image-gallery');
  imageGallery.innerHTML = '';
  
  if (pkg.images && pkg.images.length > 0) {
    pkg.images.forEach(image => {
      const imgElement = document.createElement('img');
      imgElement.src = image.image_url;
      imgElement.alt = image.description || 'Package image';
      imgElement.className = 'gallery-image';
      imageGallery.appendChild(imgElement);
    });
  } else {
    // Show placeholder
    imageGallery.innerHTML = '<img src="/placeholder.jpg" alt="No image">';
  }
  
  // Display itinerary with car dealers
  pkg.itinerary_details.forEach(day => {
    console.log(`Day ${day.day}:`);
    day.car_dealers.forEach(dealer => {
      console.log(`  Car Dealer: ${dealer.dealer_name} (ID: ${dealer.id})`);
    });
  });
}

// Load package on page load
loadPackageDetail(14);
```

---

**Last Updated:** 2024-01-15  
**API Version:** 1.0  
**Changes:** Added image support and car dealer IDs to package APIs

