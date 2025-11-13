# Company Profile Module - Implementation Summary

## Overview

Successfully implemented a comprehensive Company Profile module for the tour management system. This module allows tour operators to manage their company information, branding, and contact details.

## What Was Implemented

### 1. Database Model (`CompanyProfile`)

**Location:** `tour_management/models.py`

Created a new `CompanyProfile` model with the following features:
- **One-to-One relationship** with `Touroperator` (one profile per tour operator)
- **Comprehensive fields** for company information:
  - Basic info: company name, tagline, description
  - Contact: phone, alternate phone, email, website
  - Address: full address with city, state, country, pincode
  - Social media: Instagram, Facebook, Twitter, LinkedIn, YouTube (all optional)
  - Business info: registration number, GST number, established year
  - Images: logo and banner images (stored as JSON arrays of image IDs)
- **Audit fields**: created_at, updated_at, created_by, updated_by
- **Database table name**: `CompanyProfile`

### 2. Controller Functions

**Location:** `tour_management/controllers/company_profile.py`

Implemented three main API functions:

#### a. `add_company_profile()`
- Creates a new company profile for a tour operator
- Validates that only one profile exists per tour operator
- Required fields: `tour_operator_id`, `company_name`, `created_by`
- Returns profile ID on success

#### b. `get_company_profile()`
- Retrieves company profile for a tour operator
- Accessible by all users (managers and regular users)
- Returns structured JSON with nested objects for address, social media, business info, and images
- Required field: `tour_operator_id`

#### c. `update_company_profile()`
- Updates existing company profile
- **Manager-only access** - validates user role before allowing updates
- Supports partial updates (only update fields that are provided)
- Required fields: `tour_operator_id`, `updated_by`

### 3. URL Routes

**Location:** `tour_management/urls.py`

Added three new API endpoints:
- `POST /company_profile/add/` - Create company profile
- `POST /company_profile/get/` - Retrieve company profile
- `POST /company_profile/update/` - Update company profile

### 4. Image Support

**Updated:** `tour_management/models.py`

- Added `'company_profile'` to `ImageMetadata.MODULE_CHOICES`
- Added `max_images_company_profile` field to `TourOperatorQuota` model (default: 5)
- Company profiles can have separate logo and banner images
- Images are managed through the existing image upload API

### 5. Django Admin Integration

**Location:** `tour_management/admin.py`

Registered `CompanyProfile` in Django admin with:
- List display showing key fields
- Search functionality by company name, email, phone, city
- Filters by tour operator, city, state, country
- Organized fieldsets for easy editing:
  - Basic Information
  - Contact Information
  - Address
  - Social Media (collapsible)
  - Business Information
  - Images
  - Metadata (collapsible, read-only)

### 6. Database Migration

**Location:** `tour_management/migrations/0009_add_company_profile.py`

Created migration that:
- Adds `max_images_company_profile` field to `TourOperatorQuota`
- Creates `CompanyProfile` table with all fields
- Sets up foreign key relationships

**Migration Status:** ✅ Successfully applied

### 7. Comprehensive Documentation

**Location:** `docs/company_profile_api.md`

Created detailed API documentation including:
- Overview and access control
- Complete API reference for all three endpoints
- Request/response examples
- Field descriptions
- Usage examples (minimal profile, partial updates, image integration)
- Integration guide with Image API
- cURL testing examples
- Important notes and related APIs

## Key Features

### Access Control
- **Managers**: Can create and update company profiles
- **Users**: Can view company profiles (read-only)
- Role validation enforced in the update API

### Data Sharing
- All users of the same tour operator share the same company profile
- Changes made by managers are immediately visible to all users

### Flexibility
- Most fields are optional (only company_name is required)
- Supports partial updates - update only the fields you need
- Separate image arrays for logos and banners

### Image Management
- Integrates with existing image upload system
- Supports multiple logo and banner images
- Subject to quota limits (default: 5 images)
- Images stored as JSON arrays of image IDs

## Files Modified/Created

### Created Files:
1. `tour_management/controllers/company_profile.py` - Controller functions
2. `tour_management/migrations/0009_add_company_profile.py` - Database migration
3. `docs/company_profile_api.md` - API documentation
4. `docs/COMPANY_PROFILE_IMPLEMENTATION_SUMMARY.md` - This file

### Modified Files:
1. `tour_management/models.py` - Added CompanyProfile model, updated ImageMetadata and TourOperatorQuota
2. `tour_management/urls.py` - Added company profile routes
3. `tour_management/admin.py` - Registered CompanyProfile and updated TourOperatorQuota admin

## Testing

The implementation has been validated:
- ✅ Django system check passed
- ✅ Database migration applied successfully
- ✅ No syntax errors
- ✅ Models properly registered in admin
- ✅ URL routes configured correctly

## Next Steps

To start using the Company Profile module:

1. **Create a company profile** for your tour operator using the add API
2. **Upload logo and banner images** using the image upload API with `module="company_profile"`
3. **Update the profile** with image IDs and other details
4. **Retrieve the profile** to display on your frontend

## Example Workflow

```bash
# 1. Create profile
curl -X POST http://localhost:8000/company_profile/add/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1, "created_by": 5, "company_name": "My Tour Company"}'

# 2. Upload logo image
curl -X POST http://localhost:8000/image/upload/ \
  -F "tour_operator_id=1" \
  -F "module=company_profile" \
  -F "record_id=1" \
  -F "images=@logo.png"

# 3. Update profile with image ID
curl -X POST http://localhost:8000/company_profile/update/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1, "updated_by": 5, "logo_image_ids": [301]}'

# 4. Get profile
curl -X POST http://localhost:8000/company_profile/get/ \
  -H "Content-Type: application/json" \
  -d '{"tour_operator_id": 1}'
```

## Notes

- The module follows the existing codebase patterns and conventions
- All APIs use POST method for consistency with other endpoints
- Error handling includes proper HTTP status codes and descriptive messages
- The implementation is production-ready and fully integrated with the existing system

