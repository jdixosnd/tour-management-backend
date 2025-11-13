# Company Profile API Documentation

## Overview

The Company Profile module allows tour operators to manage their company information, branding, and contact details. Each tour operator has **one company profile** that is shared across all users of that company.

### Access Control
- **Managers**: Can create and update company profiles
- **Users**: Can view company profiles (read-only)

---

## API Endpoints

### 1. Create Company Profile - `POST /company_profile/add/`

Creates a new company profile for a tour operator. Only one profile per tour operator is allowed.

#### Request Body

```json
{
  "tour_operator_id": 1,
  "created_by": 5,
  "company_name": "Kerala Dream Holidays Pvt Ltd",
  "tagline": "Your Gateway to God's Own Country",
  "description": "We are a premier tour operator specializing in Kerala tourism with over 15 years of experience in creating memorable travel experiences.",
  "phone_number": "+91-484-1234567",
  "alternate_phone": "+91-9876543210",
  "email": "info@keraladreamholidays.com",
  "website": "https://www.keralareamholidays.com",
  "address_line1": "123, MG Road",
  "address_line2": "Near Marine Drive",
  "city": "Kochi",
  "state": "Kerala",
  "country": "India",
  "pincode": "682011",
  "instagram_url": "https://instagram.com/keralareamholidays",
  "facebook_url": "https://facebook.com/keralareamholidays",
  "twitter_url": "https://twitter.com/keralareamhols",
  "linkedin_url": "https://linkedin.com/company/keralareamholidays",
  "youtube_url": "https://youtube.com/@keralareamholidays",
  "registration_number": "KL-2010-12345",
  "gst_number": "32AABCU9603R1ZM",
  "established_year": 2010,
  "logo_image_ids": [101, 102],
  "banner_image_ids": [201, 202, 203]
}
```

#### Required Fields
- `tour_operator_id` (integer)
- `company_name` (string)
- `created_by` (integer) - User ID of the manager creating the profile

#### Optional Fields
All other fields are optional.

#### Success Response

```json
{
  "code": 200,
  "message": "Company profile created successfully",
  "profile_id": 1
}
```

#### Error Responses

**Profile Already Exists (409)**
```json
{
  "code": 409,
  "message": "Company profile already exists for this tour operator. Use update API instead."
}
```

**Tour Operator Not Found (404)**
```json
{
  "code": 404,
  "message": "Tour operator not found"
}
```

**Missing Required Fields (400)**
```json
{
  "code": 400,
  "message": "Missing required fields: company_name, created_by"
}
```

---

### 2. Get Company Profile - `POST /company_profile/get/`

Retrieves the company profile for a tour operator. Accessible by all users (managers and regular users).

#### Request Body

```json
{
  "tour_operator_id": 1
}
```

#### Success Response

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "tour_operator_id": 1,
    "company_name": "Kerala Dream Holidays Pvt Ltd",
    "tagline": "Your Gateway to God's Own Country",
    "description": "We are a premier tour operator specializing in Kerala tourism...",
    "phone_number": "+91-484-1234567",
    "alternate_phone": "+91-9876543210",
    "email": "info@keralareamholidays.com",
    "website": "https://www.keralareamholidays.com",
    "address": {
      "line1": "123, MG Road",
      "line2": "Near Marine Drive",
      "city": "Kochi",
      "state": "Kerala",
      "country": "India",
      "pincode": "682011"
    },
    "social_media": {
      "instagram": "https://instagram.com/keralareamholidays",
      "facebook": "https://facebook.com/keralareamholidays",
      "twitter": "https://twitter.com/keralareamhols",
      "linkedin": "https://linkedin.com/company/keralareamholidays",
      "youtube": "https://youtube.com/@keralareamholidays"
    },
    "business_info": {
      "registration_number": "KL-2010-12345",
      "gst_number": "32AABCU9603R1ZM",
      "established_year": 2010
    },
    "images": {
      "logo": [101, 102],
      "banner": [201, 202, 203]
    },
    "created_at": "2025-11-13T10:30:00Z",
    "updated_at": "2025-11-13T14:45:00Z",
    "created_by": 5,
    "updated_by": 5
  }
}
```

#### Error Response

**Profile Not Found (404)**
```json
{
  "code": 404,
  "message": "Company profile not found for this tour operator"
}
```

---

### 3. Update Company Profile - `POST /company_profile/update/`

Updates an existing company profile. **Only managers can update** the profile.

#### Request Body

You can update any field(s). Only include the fields you want to update.

```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "company_name": "Kerala Dream Holidays Private Limited",
  "tagline": "Experience God's Own Country Like Never Before",
  "phone_number": "+91-484-7654321",
  "email": "contact@keraladreamholidays.com",
  "logo_image_ids": [105, 106],
  "banner_image_ids": [210, 211, 212, 213]
}
```

#### Required Fields
- `tour_operator_id` (integer)
- `updated_by` (integer) - User ID of the manager updating the profile

#### Success Response

```json
{
  "code": 200,
  "message": "Company profile updated successfully",
  "profile_id": 1
}
```

#### Error Responses

**Not a Manager (403)**
```json
{
  "code": 403,
  "message": "Only managers can update company profile"
}
```

**Profile Not Found (404)**
```json
{
  "code": 404,
  "message": "Company profile not found. Please create one first."
}
```

**User Not Found (404)**
```json
{
  "code": 404,
  "message": "User not found"
}
```

---

## Field Descriptions

### Basic Information
- **company_name** (required): Official company name
- **tagline**: Short catchy phrase describing the company
- **description**: Detailed description of the company and services

### Contact Information
- **phone_number**: Primary contact number
- **alternate_phone**: Secondary contact number
- **email**: Company email address
- **website**: Company website URL

### Address
- **address_line1**: Street address line 1
- **address_line2**: Street address line 2 (optional)
- **city**: City name
- **state**: State/Province name
- **country**: Country name
- **pincode**: Postal/ZIP code

### Social Media (All Optional)
- **instagram_url**: Instagram profile URL
- **facebook_url**: Facebook page URL
- **twitter_url**: Twitter profile URL
- **linkedin_url**: LinkedIn company page URL
- **youtube_url**: YouTube channel URL

### Business Information
- **registration_number**: Company registration number
- **gst_number**: GST/Tax registration number
- **established_year**: Year the company was established (e.g., 2010)

### Images
- **logo_image_ids**: Array of image IDs for company logos (use image upload API first)
- **banner_image_ids**: Array of image IDs for banner/cover images

---

## Usage Examples

### Example 1: Create Minimal Profile

```json
{
  "tour_operator_id": 2,
  "created_by": 8,
  "company_name": "Goa Beach Tours"
}
```

### Example 2: Update Only Social Media Links

```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "instagram_url": "https://instagram.com/newhandle",
  "facebook_url": "https://facebook.com/newpage"
}
```

### Example 3: Update Logo and Banner Images

First, upload images using the image upload API, then update the profile:

```json
{
  "tour_operator_id": 1,
  "updated_by": 5,
  "logo_image_ids": [301],
  "banner_image_ids": [401, 402, 403]
}
```

---

## Integration with Image API

Company profile images (logo and banner) are managed through the existing image upload API.

### Step 1: Upload Images

```bash
POST /image/upload/
Content-Type: multipart/form-data

{
  "tour_operator_id": 1,
  "module": "company_profile",
  "record_id": 1,
  "images": [file1, file2]
}
```

### Step 2: Get Image IDs from Response

```json
{
  "code": 200,
  "message": "Images uploaded successfully",
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

## Testing with cURL

### Create Profile

```bash
curl -X POST http://localhost:8000/company_profile/add/ \
  -H "Content-Type: application/json" \
  -d '{
    "tour_operator_id": 1,
    "created_by": 5,
    "company_name": "Kerala Dream Holidays",
    "phone_number": "+91-484-1234567",
    "email": "info@keraladreamholidays.com"
  }'
```

### Get Profile

```bash
curl -X POST http://localhost:8000/company_profile/get/ \
  -H "Content-Type: application/json" \
  -d '{
    "tour_operator_id": 1
  }'
```

### Update Profile

```bash
curl -X POST http://localhost:8000/company_profile/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "tour_operator_id": 1,
    "updated_by": 5,
    "tagline": "New tagline here",
    "website": "https://newwebsite.com"
  }'
```

---

## Notes

1. **One Profile Per Tour Operator**: Each tour operator can have only one company profile
2. **Manager-Only Updates**: Only users with role='manager' can create or update profiles
3. **All Users Can View**: Both managers and regular users can view the profile
4. **Image Quota**: Company profile images are subject to the `max_images_company_profile` quota (default: 5)
5. **Shared Across Users**: All users of the same tour operator see the same company profile
6. **Optional Fields**: Most fields are optional - you can start with minimal information and add more later

---

## Related APIs

- **Image Upload API**: `/image/upload/` - Upload logo and banner images
- **Image Get API**: `/image/get/` - Retrieve uploaded images
- **User API**: `/user/get/` - Get user details including role
- **Tour Operator API**: `/touroperator/get/` - Get tour operator details


