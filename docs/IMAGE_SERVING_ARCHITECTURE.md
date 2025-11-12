# Image Serving Architecture - High Performance Solution

## Current Problem

Currently, images are served directly from Django using:
```python
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Issues with this approach:**
- ❌ Django serves files directly (slow, blocks workers)
- ❌ No caching mechanism
- ❌ Cannot handle high concurrent requests
- ❌ No CDN support
- ❌ Poor scalability
- ❌ Image paths like `/media/images/2024/01/15/image.jpg` won't work in production

---

## Recommended Solutions (3 Options)

### ✅ **Option 1: Nginx + Local Storage (Best for Self-Hosted)**

**Architecture:**
```
Frontend → Nginx (serves images) → Django (API only)
                ↓
         /media/ directory
```

**Pros:**
- ✅ Fast (Nginx serves static files efficiently)
- ✅ No external dependencies
- ✅ Built-in caching
- ✅ Can handle thousands of concurrent requests
- ✅ Low cost (no cloud storage fees)

**Cons:**
- ⚠️ Requires server storage
- ⚠️ No automatic CDN distribution
- ⚠️ Backup management needed

**Implementation:** See Section A below

---

### ✅ **Option 2: AWS S3 + CloudFront CDN (Best for Production)**

**Architecture:**
```
Frontend → CloudFront CDN → S3 Bucket
Django → S3 (upload only)
```

**Pros:**
- ✅ Globally distributed (CDN)
- ✅ Extremely scalable
- ✅ Automatic backups
- ✅ No server storage needed
- ✅ Built-in image optimization options

**Cons:**
- ⚠️ Monthly costs (storage + bandwidth)
- ⚠️ Requires AWS account

**Implementation:** See Section B below

---

### ✅ **Option 3: Hybrid - Nginx + Image Proxy API (Flexible)**

**Architecture:**
```
Frontend → /api/image/serve/{image_id} → Django → Nginx X-Accel-Redirect
```

**Pros:**
- ✅ Access control (authentication/authorization)
- ✅ Image transformations (resize, crop)
- ✅ Usage tracking
- ✅ Flexible (can switch storage backend)

**Cons:**
- ⚠️ More complex setup
- ⚠️ Slight overhead for auth checks

**Implementation:** See Section C below

---

## A. Implementation: Nginx + Local Storage

### Step 1: Update Nginx Configuration

**File:** `config/nginx/conf.d/local.conf`

```nginx
upstream tour_management_project_server {
    server tour_management:9300;
}

server {
    listen 80;
    client_max_body_size 30M;
    server_name localhost;

    # Serve media files directly from Nginx (FAST!)
    location /media/ {
        alias /tour_management_project/media/;
        expires 30d;  # Cache for 30 days
        add_header Cache-Control "public, immutable";
        access_log off;  # Don't log image requests
        
        # Enable gzip compression
        gzip on;
        gzip_types image/jpeg image/png image/gif;
    }

    # Serve static files
    location /static/ {
        alias /tour_management_project/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Proxy API requests to Django
    location / {
        proxy_pass http://tour_management_project_server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_read_timeout 300s;
    }
}
```

### Step 2: Update Docker Compose

**File:** `docker-compose.yml`

```yaml
version: '3'

services:
  tour_management:
    build: .
    volumes:
      - tour_management_project:/tour_management_project_volume
      - media_files:/tour_management_project/media  # Shared media volume
    networks:  
      - nginx_network
    environment:
      - SECRET_KEY=${tour_management_project_SECRET_KEY}
      - DOCKER=1

  nginx:
    image: nginx:1.13
    ports:
      - 9300:80
    volumes:
      - ./config/nginx/conf.d:/etc/nginx/conf.d
      - ./static:/static
      - media_files:/tour_management_project/media  # Mount same media volume
    depends_on:
      - tour_management
    networks:  
      - nginx_network
    
volumes:
  tour_management_project:
  media_files:  # Shared volume for media files

networks:  
  nginx_network:
    driver: bridge
```

### Step 3: Frontend Usage

```javascript
// Images are now served directly by Nginx
const imageUrl = packageData.images[0].image_url;
// Example: "/media/images/2024/01/15/package_cover.jpg"

// Use directly in img tag
<img src={imageUrl} alt="Package" />

// Or construct full URL if needed
const fullUrl = `${API_BASE_URL}${imageUrl}`;
// Example: "http://localhost:9300/media/images/2024/01/15/package_cover.jpg"
```

**Performance:**
- ✅ Nginx serves images directly (no Django overhead)
- ✅ Browser caches images for 30 days
- ✅ Can handle 10,000+ concurrent image requests

---

## B. Implementation: AWS S3 + CloudFront

### Step 1: Install Dependencies

```bash
pip install boto3 django-storages
```

Add to `requirements.txt`:
```
boto3==1.28.0
django-storages==1.14.0
```

### Step 2: Update Django Settings

**File:** `tour_management_project/settings.py`

```python
import os

# AWS S3 Configuration
USE_S3 = os.environ.get('USE_S3', 'False') == 'True'

if USE_S3:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # CloudFront CDN
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_CLOUDFRONT_DOMAIN', 
                                          f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com')
    
    # S3 Settings
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=2592000',  # 30 days
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False  # Don't add auth query params to URLs
    
    # Media files storage
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Local storage (development)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'storages',  # Add this
]
```

### Step 3: Environment Variables

Create `.env` file:
```bash
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=tour-management-images
AWS_S3_REGION_NAME=us-east-1
AWS_CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net  # Your CloudFront domain
```

### Step 4: AWS Setup

**S3 Bucket Configuration:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::tour-management-images/*"
    }
  ]
}
```

**CORS Configuration:**
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

### Step 5: Frontend Usage

```javascript
// Images are now served from CloudFront CDN
const imageUrl = packageData.images[0].image_url;
// Example: "https://d1234567890.cloudfront.net/media/images/2024/01/15/package.jpg"

// Use directly - globally distributed!
<img src={imageUrl} alt="Package" />
```

**Performance:**
- ✅ Global CDN distribution
- ✅ Automatic scaling
- ✅ 99.99% uptime SLA
- ✅ Can handle millions of requests

---

## C. Implementation: Image Proxy API with Access Control

### Step 1: Create Image Serving View

**File:** `tour_management/images.py`

Add this function:

```python
from django.http import FileResponse, Http404
from django.views.decorators.cache import cache_control
import os

@csrf_exempt
@cache_control(max_age=2592000, public=True)  # Cache for 30 days
def serve_image(request, image_id):
    """
    Serve image with optional access control and transformations
    """
    try:
        # Get image metadata
        image = ImageMetadata.objects.get(id=image_id)
        
        # Optional: Add access control
        # tour_operator_id = request.GET.get('tour_operator_id')
        # if image.tour_operator_id != int(tour_operator_id):
        #     return JsonResponse({"error": "Unauthorized"}, status=403)
        
        # Optional: Image transformations (resize, crop)
        width = request.GET.get('width')
        height = request.GET.get('height')
        
        if width or height:
            # Use Pillow to resize
            from PIL import Image
            import io
            
            img = Image.open(image.image_path.path)
            if width and height:
                img = img.resize((int(width), int(height)))
            elif width:
                ratio = int(width) / img.width
                img = img.resize((int(width), int(img.height * ratio)))
            
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            
            return FileResponse(img_io, content_type='image/jpeg')
        
        # Serve original image
        return FileResponse(open(image.image_path.path, 'rb'), 
                          content_type='image/jpeg')
        
    except ImageMetadata.DoesNotExist:
        raise Http404("Image not found")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
```

### Step 2: Add URL Route

**File:** `tour_management/urls.py`

```python
urlpatterns = [
    # ... existing routes
    path('image/serve/<int:image_id>/', images.serve_image, name='serve_image'),
]
```

### Step 3: Update API Response

Modify `get_images()` helper to return API URLs instead of file paths:

```python
def get_images(module, record_id, include_binary=False):
    # ... existing code
    
    image_data = {
        "id": image.id,
        "description": image.description,
        "order": image.order,
        "image_url": f"/image/serve/{image.id}/"  # API endpoint instead of file path
    }
```

### Step 4: Frontend Usage

```javascript
// Images served via API with optional transformations
const imageId = packageData.images[0].id;

// Original size
const originalUrl = `/image/serve/${imageId}/`;

// Resized (thumbnail)
const thumbnailUrl = `/image/serve/${imageId}/?width=300&height=200`;

// Use in img tag
<img src={originalUrl} alt="Package" />
<img src={thumbnailUrl} alt="Thumbnail" />
```

**Benefits:**
- ✅ Access control (can check permissions)
- ✅ On-the-fly image resizing
- ✅ Usage tracking
- ✅ Can add watermarks, filters, etc.

---

## Performance Comparison

| Solution | Requests/sec | Latency | Scalability | Cost |
|----------|-------------|---------|-------------|------|
| **Current (Django static)** | ~100 | 50-100ms | Poor | Free |
| **Option 1 (Nginx)** | ~10,000 | 5-10ms | Good | Free |
| **Option 2 (S3+CDN)** | Unlimited | 10-50ms | Excellent | $10-100/mo |
| **Option 3 (Proxy API)** | ~1,000 | 20-50ms | Medium | Free |

---

## Recommendation

### For Development:
Use **Option 1 (Nginx)** - Simple, fast, no external dependencies

### For Production:
Use **Option 2 (S3 + CloudFront)** if:
- You expect high traffic (>10,000 users)
- You need global distribution
- Budget allows ($50-200/month)

Use **Option 1 (Nginx)** if:
- Self-hosted infrastructure
- Lower traffic (<10,000 users)
- Want to minimize costs

Use **Option 3 (Proxy API)** if:
- Need access control
- Want image transformations
- Need usage analytics

---

## Migration Path

### Phase 1: Immediate (Nginx)
1. Update nginx config to serve `/media/` directly
2. Update docker-compose to share media volume
3. Test image loading

### Phase 2: Optional (S3)
1. Create S3 bucket and CloudFront distribution
2. Install django-storages
3. Update settings with S3 credentials
4. Migrate existing images to S3
5. Switch `USE_S3=True`

### Phase 3: Advanced (Proxy API)
1. Implement serve_image endpoint
2. Add access control logic
3. Add image transformation features
4. Update frontend to use new endpoints

---

## Next Steps

**Choose your solution and I can help implement it:**

1. **Quick Win (30 minutes)**: Implement Option 1 (Nginx) - Update nginx config and docker-compose
2. **Production Ready (2 hours)**: Implement Option 2 (S3 + CloudFront) - Full cloud setup
3. **Advanced (4 hours)**: Implement Option 3 (Proxy API) - Custom image serving with features

Which option would you like to implement?

