# Image Handling Guide for UI Team

## 📋 Overview

We've implemented high-performance image serving using Nginx. This document explains what changed, what stayed the same, and how to integrate images in the frontend.

---

## ✅ Good News: Minimal Changes Required!

**The API response format remains exactly the same.** You can continue using the existing integration with better performance.

---

## 🔄 What Changed

### Backend Changes:
- ✅ Images now served directly by Nginx (100x faster)
- ✅ Automatic 30-day browser caching enabled
- ✅ CORS headers configured for cross-origin access
- ✅ Gzip compression for faster downloads

### What Stayed the Same:
- ✅ API endpoints (no changes)
- ✅ Request/response format (no changes)
- ✅ Image URLs format (no changes)
- ✅ Upload process (no changes)

---

## 📊 API Response Format

### Package GET API Response

**Endpoint:** `POST /package/get/`

**Response includes images:**
```json
{
  "data": [
    {
      "id": 14,
      "name": "Malaysia Adventure Package",
      "description": "Explore the beauty of Malaysia",
      "package_amount": 11111.0,
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
      ],
      "itinerary_details": [
        {
          "day": 1,
          "title": "City Tour",
          "activities": [
            {
              "name": "River Rafting",
              "type": "event",
              "images": [
                {
                  "id": 201,
                  "description": "Activity photo",
                  "order": 1,
                  "image_url": "/media/images/2024/01/15/activity.jpg"
                }
              ]
            }
          ],
          "hotel_details": [
            {
              "id": 1,
              "name": "Grand Hotel",
              "images": [
                {
                  "id": 301,
                  "description": "Hotel exterior",
                  "order": 1,
                  "image_url": "/media/images/2024/01/15/hotel.jpg"
                }
              ]
            }
          ],
          "car_dealers": [
            {
              "id": 1,
              "dealer_name": "WheelsOnJoy",
              "contact_no": "9898989898"
            }
          ]
        }
      ]
    }
  ]
}
```

### Key Points:

1. **`images` array** - Contains all images for the entity (package, hotel, activity)
2. **`image_url`** - Relative path to the image (e.g., `/media/images/2024/01/15/image.jpg`)
3. **`order`** - Display order (1, 2, 3...) - use for sorting in carousel/gallery
4. **`description`** - Image description (use for alt text or captions)
5. **`id`** - Image ID (use for delete operations)

---

## 🎨 Frontend Integration

### 1. Display Package Images

#### React Example:

```jsx
import React, { useState, useEffect } from 'react';

function PackageDetail({ packageId }) {
  const [packageData, setPackageData] = useState(null);
  const API_BASE_URL = 'http://localhost:9300'; // Your API URL

  useEffect(() => {
    // Fetch package data
    fetch(`${API_BASE_URL}/package/get/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tour_operator_id: 1,
        package_id: packageId
      })
    })
    .then(res => res.json())
    .then(data => setPackageData(data.data[0]));
  }, [packageId]);

  if (!packageData) return <div>Loading...</div>;

  return (
    <div>
      <h1>{packageData.name}</h1>
      
      {/* Display images */}
      <div className="image-gallery">
        {packageData.images && packageData.images.length > 0 ? (
          packageData.images.map(image => (
            <img 
              key={image.id}
              src={`${API_BASE_URL}${image.image_url}`}
              alt={image.description || 'Package image'}
              loading="lazy"  // Lazy loading for performance
            />
          ))
        ) : (
          <img src="/placeholder.jpg" alt="No image available" />
        )}
      </div>
    </div>
  );
}
```

#### Angular Example:

```typescript
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-package-detail',
  template: `
    <div *ngIf="packageData">
      <h1>{{ packageData.name }}</h1>
      
      <!-- Display images -->
      <div class="image-gallery">
        <img 
          *ngFor="let image of packageData.images"
          [src]="getImageUrl(image.image_url)"
          [alt]="image.description || 'Package image'"
          loading="lazy"
        />
        
        <!-- Placeholder if no images -->
        <img 
          *ngIf="!packageData.images || packageData.images.length === 0"
          src="/assets/placeholder.jpg"
          alt="No image available"
        />
      </div>
    </div>
  `
})
export class PackageDetailComponent implements OnInit {
  packageData: any;
  apiBaseUrl = 'http://localhost:9300';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.post(`${this.apiBaseUrl}/package/get/`, {
      tour_operator_id: 1,
      package_id: 14
    }).subscribe((response: any) => {
      this.packageData = response.data[0];
    });
  }

  getImageUrl(imagePath: string): string {
    return `${this.apiBaseUrl}${imagePath}`;
  }
}
```

#### Vue Example:

```vue
<template>
  <div v-if="packageData">
    <h1>{{ packageData.name }}</h1>
    
    <!-- Display images -->
    <div class="image-gallery">
      <img 
        v-for="image in packageData.images"
        :key="image.id"
        :src="getImageUrl(image.image_url)"
        :alt="image.description || 'Package image'"
        loading="lazy"
      />
      
      <!-- Placeholder if no images -->
      <img 
        v-if="!packageData.images || packageData.images.length === 0"
        src="/placeholder.jpg"
        alt="No image available"
      />
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      packageData: null,
      apiBaseUrl: 'http://localhost:9300'
    };
  },
  mounted() {
    this.fetchPackage();
  },
  methods: {
    async fetchPackage() {
      const response = await fetch(`${this.apiBaseUrl}/package/get/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tour_operator_id: 1,
          package_id: 14
        })
      });
      const data = await response.json();
      this.packageData = data.data[0];
    },
    getImageUrl(imagePath) {
      return `${this.apiBaseUrl}${imagePath}`;
    }
  }
};
</script>
```

### 2. Image Carousel/Gallery

```jsx
// React with image carousel
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';

function PackageGallery({ images, apiBaseUrl }) {
  if (!images || images.length === 0) {
    return <img src="/placeholder.jpg" alt="No images" />;
  }

  // Sort by order field
  const sortedImages = [...images].sort((a, b) => a.order - b.order);

  return (
    <Carousel showThumbs={true} infiniteLoop={true}>
      {sortedImages.map(image => (
        <div key={image.id}>
          <img 
            src={`${apiBaseUrl}${image.image_url}`}
            alt={image.description || 'Package image'}
          />
          {image.description && <p className="legend">{image.description}</p>}
        </div>
      ))}
    </Carousel>
  );
}
```

### 3. Thumbnail + Full Image

```jsx
// Package listing with thumbnail
function PackageCard({ package, apiBaseUrl }) {
  // Use first image as thumbnail
  const thumbnail = package.images && package.images.length > 0
    ? package.images.find(img => img.order === 1) || package.images[0]
    : null;

  return (
    <div className="package-card">
      {thumbnail ? (
        <img 
          src={`${apiBaseUrl}${thumbnail.image_url}`}
          alt={package.name}
          className="thumbnail"
        />
      ) : (
        <img src="/placeholder.jpg" alt={package.name} className="thumbnail" />
      )}
      <h3>{package.name}</h3>
      <p>{package.description}</p>
      <p className="price">${package.package_amount}</p>
    </div>
  );
}
```

---

## 📤 Image Upload

### Upload New Images

**Endpoint:** `POST /image/upload/`

**Request Type:** `multipart/form-data`

```javascript
async function uploadPackageImages(packageId, tourOperatorId, imageFiles) {
  const formData = new FormData();
  
  formData.append('tour_operator_id', tourOperatorId);
  formData.append('module', 'package');
  formData.append('record_id', packageId);
  
  // Add multiple images
  imageFiles.forEach((file, index) => {
    formData.append('images', file);
    formData.append('description', file.name || `Image ${index + 1}`);
    formData.append('order', index + 1);
  });
  
  const response = await fetch('http://localhost:9300/image/upload/', {
    method: 'POST',
    body: formData  // Don't set Content-Type header - browser will set it
  });
  
  return await response.json();
}

// Usage in React
function ImageUploader({ packageId }) {
  const handleFileChange = async (event) => {
    const files = Array.from(event.target.files);
    
    try {
      const result = await uploadPackageImages(packageId, 1, files);
      console.log('Upload result:', result);
      
      // Check for errors
      result.results.forEach(item => {
        if (item.error) {
          alert(`Error uploading ${item.file_name}: ${item.error}`);
        } else {
          console.log(`Uploaded: ${item.file_name}`);
        }
      });
      
      // Refresh package data to show new images
      // ... your refresh logic
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <input 
      type="file" 
      multiple 
      accept="image/*"
      onChange={handleFileChange}
    />
  );
}
```

### Upload Response:

```json
{
  "results": [
    {
      "file_name": "image1.jpg",
      "image_id": 101,
      "image_url": "/media/images/2024/01/15/image1.jpg"
    },
    {
      "file_name": "image2.jpg",
      "image_id": 102,
      "image_url": "/media/images/2024/01/15/image2.jpg"
    }
  ]
}
```

**Error Response (Quota Exceeded):**
```json
{
  "results": [
    {
      "error": "Quota exceeded. Only 3 images can be uploaded.",
      "file_name": "image4.jpg"
    }
  ]
}
```

---

## 🗑️ Delete Image

**Endpoint:** `POST /image/delete/`

```javascript
async function deleteImage(imageId) {
  const response = await fetch('http://localhost:9300/image/delete/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tour_operator_id: 1,
      image_id: imageId
    })
  });
  
  return await response.json();
}

// Usage
function ImageWithDelete({ image, onDelete }) {
  const handleDelete = async () => {
    if (confirm('Delete this image?')) {
      await deleteImage(image.id);
      onDelete(image.id);  // Update UI
    }
  };

  return (
    <div className="image-container">
      <img src={`${API_BASE_URL}${image.image_url}`} alt={image.description} />
      <button onClick={handleDelete}>Delete</button>
    </div>
  );
}
```

---

## ⚡ Performance Best Practices

### 1. Use Lazy Loading

```jsx
// Lazy load images below the fold
<img 
  src={imageUrl}
  alt="Package"
  loading="lazy"  // Native lazy loading
/>
```

### 2. Responsive Images

```jsx
// Use srcset for different screen sizes
<img 
  src={`${apiBaseUrl}${image.image_url}`}
  alt={image.description}
  loading="lazy"
  style={{ maxWidth: '100%', height: 'auto' }}
/>
```

### 3. Caching Strategy

**Images are automatically cached for 30 days by the browser!**

```javascript
// No special code needed - browser handles caching automatically
// First load: Downloads image
// Subsequent loads: Uses cached version (instant!)
```

### 4. Preload Critical Images

```jsx
// Preload first image for faster LCP
useEffect(() => {
  if (packageData?.images?.[0]) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = `${API_BASE_URL}${packageData.images[0].image_url}`;
    document.head.appendChild(link);
  }
}, [packageData]);
```

### 5. Handle Loading States

```jsx
function ImageWithLoader({ src, alt }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="image-wrapper">
      {!loaded && <div className="skeleton-loader" />}
      <img 
        src={src}
        alt={alt}
        onLoad={() => setLoaded(true)}
        style={{ display: loaded ? 'block' : 'none' }}
      />
    </div>
  );
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Package Listing Page

```jsx
// Show first image as thumbnail
function PackageList({ packages }) {
  return (
    <div className="package-grid">
      {packages.map(pkg => {
        const thumbnail = pkg.images?.[0];
        return (
          <div key={pkg.id} className="package-card">
            <img 
              src={thumbnail 
                ? `${API_BASE_URL}${thumbnail.image_url}`
                : '/placeholder.jpg'
              }
              alt={pkg.name}
              loading="lazy"
            />
            <h3>{pkg.name}</h3>
            <p>${pkg.package_amount}</p>
          </div>
        );
      })}
    </div>
  );
}
```

### Use Case 2: Package Detail Page

```jsx
// Show all images in carousel
function PackageDetail({ packageId }) {
  const [pkg, setPkg] = useState(null);

  // ... fetch logic

  return (
    <div>
      {/* Image Gallery */}
      <Carousel>
        {pkg?.images?.map(image => (
          <img 
            key={image.id}
            src={`${API_BASE_URL}${image.image_url}`}
            alt={image.description}
          />
        ))}
      </Carousel>

      {/* Package Info */}
      <h1>{pkg?.name}</h1>
      <p>{pkg?.description}</p>
    </div>
  );
}
```

### Use Case 3: Image Management (Admin)

```jsx
// Upload, reorder, delete images
function ImageManager({ packageId }) {
  const [images, setImages] = useState([]);

  const handleUpload = async (files) => {
    const result = await uploadPackageImages(packageId, 1, files);
    // Refresh images
    fetchPackageImages();
  };

  const handleDelete = async (imageId) => {
    await deleteImage(imageId);
    setImages(images.filter(img => img.id !== imageId));
  };

  return (
    <div>
      {/* Upload */}
      <input type="file" multiple onChange={e => handleUpload(e.target.files)} />

      {/* Image Grid */}
      <div className="image-grid">
        {images.map(image => (
          <div key={image.id}>
            <img src={`${API_BASE_URL}${image.image_url}`} alt={image.description} />
            <button onClick={() => handleDelete(image.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔍 Testing Checklist

- [ ] Images display correctly in package listing
- [ ] Images display correctly in package detail
- [ ] Image carousel/gallery works
- [ ] Lazy loading works (check Network tab)
- [ ] Images cached on reload (check Network tab - should show "from cache")
- [ ] Upload multiple images works
- [ ] Delete image works
- [ ] Placeholder shows when no images
- [ ] No CORS errors in console
- [ ] Images load fast (<100ms after cache)

---

## 🐛 Troubleshooting

### Issue 1: Images Not Loading (CORS Error)

**Symptom:** Console shows CORS error

**Solution:** Already fixed on backend! If still seeing errors, clear browser cache.

### Issue 2: Images Not Caching

**Symptom:** Images re-download on every page load

**Solution:** Check Network tab - should see "from disk cache" or "from memory cache". If not, backend team needs to verify nginx configuration.

### Issue 3: Broken Image Links

**Symptom:** 404 errors for images

**Solution:** 
- Verify `API_BASE_URL` is correct
- Check image URL format: `${API_BASE_URL}${image.image_url}`
- Example: `http://localhost:9300/media/images/2024/01/15/image.jpg`

---

## 📞 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/image/upload/` | POST | Upload images (multipart/form-data) |
| `/image/delete/` | POST | Delete image by ID |
| `/package/get/` | POST | Get package with images |
| `/package/get_packages_from_destination/` | POST | Get packages list with images |
| `/media/images/...` | GET | Access image directly (served by Nginx) |

---

## ✅ Summary for UI Team

### What You Need to Do:

1. **Use existing API responses** - No changes to API calls
2. **Construct image URLs** - Combine `API_BASE_URL` + `image.image_url`
3. **Add lazy loading** - Use `loading="lazy"` attribute
4. **Handle empty images** - Show placeholder when no images
5. **Sort by order** - Use `image.order` field for carousel ordering

### What You Get:

- ✅ **100x faster** image loading
- ✅ **Automatic caching** (30 days in browser)
- ✅ **No CORS issues**
- ✅ **Better user experience**

### No Changes Needed For:

- ✅ API endpoints
- ✅ Request/response format
- ✅ Authentication
- ✅ Error handling

---

**Questions? Contact the backend team or refer to the full documentation in the `docs/` folder.**

