# Company Profile - Quick Start Guide

## What is Company Profile?

A module that allows tour operators to manage their company information including:
- Company name, tagline, and description
- Contact details (phone, email, website)
- Full address
- Social media links (Instagram, Facebook, Twitter, LinkedIn, YouTube)
- Business information (registration number, GST, established year)
- Logo and banner images

## Key Points

✅ **One profile per tour operator** - All users share the same profile  
✅ **Managers can edit** - Only users with role='manager' can create/update  
✅ **Everyone can view** - All users can retrieve the profile  
✅ **Flexible fields** - Only company_name is required, everything else is optional  

---

## API Endpoints

### 1. Create Profile
```
POST /company_profile/add/
```

**Minimal Request:**
```json
{
  "tour_operator_id": 1,
  "created_by": 5,
  "company_name": "Kerala Dream Holidays"
}
```

**Full Request Example:**
```json
{
  "tour_operator_id": 1,
  "created_by": 5,
  "company_name": "Kerala Dream Holidays Pvt Ltd",
  "tagline": "Your Gateway to God's Own Country",
  "description": "Premier tour operator specializing in Kerala tourism",
  "phone_number": "+91-484-1234567",
  "email": "info@keraladreamholidays.com",
  "website": "https://www.keraladreamholidays.com",
  "city": "Kochi",
  "state": "Kerala",
  "country": "India",
  "instagram_url": "https://instagram.com/keraladreamholidays",
  "facebook_url": "https://facebook.com/keraladreamholidays"
}
```

---

### 2. Get Profile
```
POST /company_profile/get/
```

**Request:**
```json
{
  "tour_operator_id": 1
}
```

**Response:**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "company_name": "Kerala Dream Holidays Pvt Ltd",
    "tagline": "Your Gateway to God's Own Country",
    "phone_number": "+91-484-1234567",
    "email": "info@keraladreamholidays.com",
    "address": {
      "line1": "123, MG Road",
      "city": "Kochi",
      "state": "Kerala",
      "country": "India"
    },
    "social_media": {
      "instagram": "https://instagram.com/keraladreamholidays",
      "facebook": "https://facebook.com/keraladreamholidays"
    },
    "images": {
      "logo": [101],
      "banner": [201, 202]
    }
  }
}
```

---

### 3. Update Profile
```
POST /company_profile/update/
```

**Request (partial update):**
```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "tagline": "New tagline here",
  "phone_number": "+91-484-9999999",
  "logo_image_ids": [105]
}
```

**Note:** Only include fields you want to update. `updated_by` must be a manager.

---

## Working with Images

### Step 1: Upload Images
```bash
POST /image/upload/

Form Data:
- tour_operator_id: 1
- module: "company_profile"
- record_id: 1
- images: [file1, file2]
```

### Step 2: Get Image IDs from Response
```json
{
  "code": 200,
  "image_ids": [301, 302]
}
```

### Step 3: Update Profile with Image IDs
```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "logo_image_ids": [301],
  "banner_image_ids": [302]
}
```

---

## Common Use Cases

### Use Case 1: Create Basic Profile
```json
{
  "tour_operator_id": 1,
  "created_by": 5,
  "company_name": "My Tour Company",
  "phone_number": "+91-1234567890",
  "email": "info@mytourcompany.com"
}
```

### Use Case 2: Add Social Media Links Later
```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "instagram_url": "https://instagram.com/mytourcompany",
  "facebook_url": "https://facebook.com/mytourcompany"
}
```

### Use Case 3: Update Logo Only
```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "logo_image_ids": [401]
}
```

---

## Error Handling

### Profile Already Exists
```json
{
  "code": 409,
  "message": "Company profile already exists for this tour operator. Use update API instead."
}
```
**Solution:** Use the update API instead of add.

### Not a Manager
```json
{
  "code": 403,
  "message": "Only managers can update company profile"
}
```
**Solution:** Ensure the `updated_by` user has role='manager'.

### Profile Not Found
```json
{
  "code": 404,
  "message": "Company profile not found for this tour operator"
}
```
**Solution:** Create a profile first using the add API.

---

## Tips

💡 **Start Simple:** Create profile with just company_name, then add details later  
💡 **Partial Updates:** You can update one field at a time  
💡 **Image Limits:** Default quota is 5 images for company profile  
💡 **Shared Data:** All users see the same profile - changes are instant  
💡 **Manager Only:** Only managers can create/update, but everyone can view  

---

## Full Documentation

For complete API reference, see: `docs/company_profile_api.md`

