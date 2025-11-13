# Company Profile API - UI Team Integration Guide

## Overview

The Company Profile module allows tour operators to manage their company information. Each tour operator has **ONE company profile** shared by all users.

**Access Rules:**
- 👁️ **All users** can VIEW the profile
- ✏️ **Only MANAGERS** can CREATE or UPDATE the profile

---

## API Endpoints

Base URL: `http://your-backend-url`

### 1️⃣ Get Company Profile (View)

**Endpoint:** `POST /company_profile/get/`

**When to use:** Display company info on dashboard, settings page, or public profile

**Request:**
```json
{
  "tour_operator_id": 1,
  "include_binary": false
}
```

**Note:** `include_binary` is optional (default: false). Set to `true` to get base64-encoded image data.

**Response:**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "tour_operator_id": 1,
    "company_name": "Kerala Dream Holidays Pvt Ltd",
    "tagline": "Your Gateway to God's Own Country",
    "description": "We are a premier tour operator...",
    "phone_number": "+91-484-1234567",
    "alternate_phone": "+91-9876543210",
    "email": "info@keraladreamholidays.com",
    "website": "https://www.keraladreamholidays.com",
    "address": {
      "line1": "123, MG Road",
      "line2": "Near Marine Drive",
      "city": "Kochi",
      "state": "Kerala",
      "country": "India",
      "pincode": "682011"
    },
    "social_media": {
      "instagram": "https://instagram.com/keraladreamholidays",
      "facebook": "https://facebook.com/keraladreamholidays",
      "twitter": "https://twitter.com/keraladreamhols",
      "linkedin": "https://linkedin.com/company/keraladreamholidays",
      "youtube": "https://youtube.com/@keraladreamholidays"
    },
    "business_info": {
      "registration_number": "KL-2010-12345",
      "gst_number": "32AABCU9603R1ZM",
      "established_year": 2010
    },
    "images": {
      "logo": [
        {
          "id": 101,
          "description": "Company Logo",
          "order": 0,
          "image_url": "/media/images/2025/11/13/logo.png"
        }
      ],
      "banner": [
        {
          "id": 201,
          "description": "Main Banner",
          "order": 0,
          "image_url": "/media/images/2025/11/13/banner1.jpg"
        },
        {
          "id": 202,
          "description": "Secondary Banner",
          "order": 1,
          "image_url": "/media/images/2025/11/13/banner2.jpg"
        }
      ]
    },
    "created_at": "2025-11-13T10:30:00Z",
    "updated_at": "2025-11-13T14:45:00Z"
  }
}
```

**Error Response (Profile not found):**
```json
{
  "code": 404,
  "message": "Company profile not found for this tour operator"
}
```

---

### 2️⃣ Create Company Profile (First Time Setup)

**Endpoint:** `POST /company_profile/add/`

**When to use:** First-time setup wizard or when profile doesn't exist

**⚠️ Important:** Only call this if profile doesn't exist. Check with GET first.

**Minimum Required Request:**
```json
{
  "tour_operator_id": 1,
  "created_by": 5,
  "company_name": "My Tour Company"
}
```

**Full Request Example:**
```json
{
  "tour_operator_id": 1,
  "created_by": 5,
  "company_name": "Kerala Dream Holidays Pvt Ltd",
  "tagline": "Your Gateway to God's Own Country",
  "description": "We are a premier tour operator specializing in Kerala tourism",
  "phone_number": "+91-484-1234567",
  "alternate_phone": "+91-9876543210",
  "email": "info@keraladreamholidays.com",
  "website": "https://www.keraladreamholidays.com",
  "address_line1": "123, MG Road",
  "address_line2": "Near Marine Drive",
  "city": "Kochi",
  "state": "Kerala",
  "country": "India",
  "pincode": "682011",
  "instagram_url": "https://instagram.com/keraladreamholidays",
  "facebook_url": "https://facebook.com/keraladreamholidays",
  "twitter_url": "https://twitter.com/keraladreamhols",
  "linkedin_url": "https://linkedin.com/company/keraladreamholidays",
  "youtube_url": "https://youtube.com/@keraladreamholidays",
  "registration_number": "KL-2010-12345",
  "gst_number": "32AABCU9603R1ZM",
  "established_year": 2010
}
```

**Success Response:**
```json
{
  "code": 200,
  "message": "Company profile created successfully",
  "profile_id": 1
}
```

**Error Response (Already exists):**
```json
{
  "code": 409,
  "message": "Company profile already exists for this tour operator. Use update API instead."
}
```

---

### 3️⃣ Update Company Profile (Edit)

**Endpoint:** `POST /company_profile/update/`

**When to use:** Edit company settings page

**⚠️ Important:** User must be a MANAGER (role='manager')

**Request (Update any fields):**
```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "company_name": "Updated Company Name",
  "tagline": "New tagline",
  "phone_number": "+91-484-9999999",
  "email": "newemail@company.com"
}
```

**Success Response:**
```json
{
  "code": 200,
  "message": "Company profile updated successfully",
  "profile_id": 1
}
```

**Error Response (Not a manager):**
```json
{
  "code": 403,
  "message": "Only managers can update company profile"
}
```

---

## Working with Images

### Step 1: Upload Logo/Banner Images

Use the existing image upload API:

**Endpoint:** `POST /image/upload/`

**Request (multipart/form-data):**
```
tour_operator_id: 1
module: "company_profile"
record_id: 1
images: [file1, file2]
```

**Response:**
```json
{
  "code": 200,
  "message": "Images uploaded successfully",
  "image_ids": [301, 302, 303]
}
```

### Step 2: Update Profile with Image IDs

**Request:**
```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "logo_image_ids": [301],
  "banner_image_ids": [302, 303]
}
```

### Step 3: Display Images

Use the image get API to retrieve image URLs:

**Endpoint:** `POST /image/get/`

**Request:**
```json
{
  "tour_operator_id": 1,
  "module": "company_profile",
  "record_id": 1
}
```

---

## UI Implementation Guide

### 1. Company Profile Settings Page

**On Page Load:**
```javascript
// 1. Get company profile
const response = await fetch('/company_profile/get/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ tour_operator_id: currentUser.tour_operator_id })
});

const result = await response.json();

if (result.code === 404) {
  // Profile doesn't exist - show "Create Profile" form
  showCreateProfileForm();
} else {
  // Profile exists - show edit form with data
  populateForm(result.data);
}
```

**On Save (Manager Only):**
```javascript
// Check if user is manager
if (currentUser.role !== 'manager') {
  alert('Only managers can update company profile');
  return;
}

// Update profile
const response = await fetch('/company_profile/update/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tour_operator_id: currentUser.tour_operator_id,
    updated_by: currentUser.id,
    company_name: formData.companyName,
    tagline: formData.tagline,
    phone_number: formData.phone,
    // ... other fields
  })
});
```

### 2. Display Company Info (Dashboard/Header)

```javascript
// Get profile
const response = await fetch('/company_profile/get/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ tour_operator_id: currentUser.tour_operator_id })
});

const result = await response.json();

if (result.code === 200) {
  // Display company name, logo, etc.
  document.getElementById('companyName').textContent = result.data.company_name;
  document.getElementById('companyTagline').textContent = result.data.tagline;

  // Display logo (if exists) - images now include URLs!
  if (result.data.images.logo.length > 0) {
    const logoImage = result.data.images.logo[0];
    document.getElementById('companyLogo').src = logoImage.image_url;
    document.getElementById('companyLogo').alt = logoImage.description || 'Company Logo';
  }

  // Display banner (if exists)
  if (result.data.images.banner.length > 0) {
    const bannerImage = result.data.images.banner[0];
    document.getElementById('companyBanner').src = bannerImage.image_url;
  }
}
```

---

## Field Reference

### Required Fields
- `company_name` - Company name (required when creating)

### Optional Fields (All can be null/empty)
- `tagline` - Short company tagline
- `description` - Detailed company description
- `phone_number` - Primary phone
- `alternate_phone` - Secondary phone
- `email` - Company email
- `website` - Company website URL
- `address_line1` - Address line 1
- `address_line2` - Address line 2
- `city` - City name
- `state` - State/Province
- `country` - Country name
- `pincode` - Postal code
- `instagram_url` - Instagram profile URL
- `facebook_url` - Facebook page URL
- `twitter_url` - Twitter profile URL
- `linkedin_url` - LinkedIn company page URL
- `youtube_url` - YouTube channel URL
- `registration_number` - Company registration number
- `gst_number` - GST/Tax number
- `established_year` - Year established (e.g., 2010)
- `logo_image_ids` - Array of logo image IDs
- `banner_image_ids` - Array of banner image IDs

---

## Important Notes for UI Team

✅ **Always check user role** before showing edit/update buttons (only managers can edit)  
✅ **Handle 404 gracefully** - Show "Create Profile" option if profile doesn't exist  
✅ **Partial updates supported** - Only send fields that changed  
✅ **All fields optional** except company_name when creating  
✅ **Image IDs are arrays** - Can have multiple logos/banners  
✅ **Use existing image APIs** for upload/display  
✅ **Profile is shared** - Changes are visible to all users immediately  

---

## Common UI Flows

### Flow 1: First Time Setup (No Profile Exists)
1. User logs in → Check if profile exists (GET)
2. If 404 → Show "Complete Your Profile" wizard
3. Manager fills form → Call ADD API
4. Success → Redirect to dashboard

### Flow 2: View Profile (Regular User)
1. User navigates to settings
2. Call GET API
3. Display profile in read-only mode
4. Show message: "Contact your manager to update profile"

### Flow 3: Edit Profile (Manager)
1. Manager navigates to settings
2. Call GET API
3. Display profile in editable form
4. Manager makes changes → Call UPDATE API
5. Success → Show success message

### Flow 4: Upload Logo
1. Manager selects logo file
2. Upload using image API (module="company_profile")
3. Get image ID from response
4. Call UPDATE API with logo_image_ids: [newImageId]
5. Display new logo

---

## Testing Tips

**Test with Postman/cURL:**
```bash
# Get profile
curl -X POST http://localhost:8000/company_profile/get/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1}'

# Create profile
curl -X POST http://localhost:8000/company_profile/add/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1, "created_by": 5, "company_name": "Test Company"}'

# Update profile
curl -X POST http://localhost:8000/company_profile/update/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1, "updated_by": 5, "tagline": "New tagline"}'
```

---

## Troubleshooting

### Issue: Image upload returns "Table doesn't exist" error

**Error:**
```json
{
  "error": "(1146, \"Table 'tour_management_db.TourOperatorQuota' doesn't exist\")"
}
```

**Solution:** This has been fixed. The TourOperatorQuota model was updated to use the correct table name. Clear your Python cache and restart the server:

```bash
# Clear cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Restart server
python manage.py runserver
```

---

## Questions?

For detailed API documentation, see: `docs/company_profile_api.md`
