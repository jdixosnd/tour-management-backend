# Complete PDF Data Structure - All Available Fields

## Overview
This document lists ALL data fields available in the Lead PDF context for use in the HTML template.

---

## 1. LEAD DATA (`lead`)

### Basic Lead Info
- `lead.lead_id` - Lead ID
- `lead.status` - Lead status (new, followup, active, closed, cancelled)
- `lead.created_at` - Lead creation timestamp

---

## 2. CUSTOMER DATA (`customer`)

### Customer Fields
- `customer.id` - Customer ID
- `customer.name` - Full customer name
- `customer.first_name` - First name (split from full name)
- `customer.last_name` - Last name (split from full name)
- `customer.email` - Customer email
- `customer.mobileno` - Customer mobile number
- `customer.company` - Customer company name (optional)
- `customer.address` - Customer address (optional)

---

## 3. PACKAGE DATA (`package`)

### Basic Package Info
- `package.id` - Package ID
- `package.name` - Package name
- `package.description` - Package description
- `package.type` - Package type (family, couple, honeymoon, group)
- `package.pax_size` - Number of people
- `package.no_of_days` - Number of days
- `package.package_amount` - Total package price
- `package.contains_travel_fare` - Boolean, includes travel fare
- `package.transport_type` - Type of transportation
- `package.terms_and_conditions` - Terms and conditions text
- `package.notes` - Additional notes
- `package.destination_id` - Destination ID

### Package Images (`package.images[]`)
Each image object contains:
- `image.id` - Image ID
- `image.image_url` - Absolute file path (converted for PDF)
- `image.description` - Image description
- `image.order` - Display order

### Package Inclusions (`package.inclusions[]`)
Each inclusion object contains:
- `inclusion.id` - Inclusion ID
- `inclusion.name` - Inclusion name
- `inclusion.description` - Inclusion description
- `inclusion.type` - Type of inclusion

### Package Exclusions (`package.exclusions[]`)
Each exclusion object contains:
- `exclusion.id` - Exclusion ID
- `exclusion.name` - Exclusion name
- `exclusion.description` - Exclusion description
- `exclusion.type` - Type of exclusion

### Package Amenities (`package.amenities[]`)
Each amenity object contains:
- `amenity.id` - Amenity ID
- `amenity.name` - Amenity name
- `amenity.description` - Amenity description
- `amenity.type` - Type of amenity

### Package Policies (`package.policies[]`)
Each policy object contains:
- `policy.id` - Policy ID
- `policy.name` - Policy name
- `policy.description` - Policy description
- `policy.type` - Type of policy

---

## 4. ITINERARY DATA (`package.itinerary_details[]`)

### Day-wise Itinerary
Each day object contains:

#### Basic Day Info
- `day.day` - Day number
- `day.city` - City name
- `day.state` - State name
- `day.title` - Day title
- `day.description` - Day description
- `day.note` - Additional notes for the day

#### Hotel Options for the Day (`day.hotel_details[]`)
Each hotel object contains:
- `hotel.id` - Hotel ID
- `hotel.name` - Hotel name
- `hotel.description` - Hotel description
- `hotel.rating` - Hotel rating (decimal)
- `hotel.website` - Hotel website URL
- `hotel.phoneno` - Hotel phone number
- `hotel.location` - Location object with:
  - `location.city` - City
  - `location.state` - State
  - `location.country` - Country
  - `location.address` - Full address
- `hotel.images[]` - Array of hotel images (same structure as package images)
- `hotel.rooms[]` - Array of room options (see below)

#### Room Options (`hotel.rooms[]`)
Each room object contains:
- `room.id` - Room ID
- `room.name` - Room name
- `room.type` - Room type (studio, standard, delux, suite, superior, family, executive, villa)
- `room.capacity` - Room capacity (number of people)
- `room.bedtype` - Bed type (single, twin, double, queen, king, bunk, rollaway, trundle, daybed)
- `room.description` - Room description
- `room.rating` - Room rating
- `room.price_per_night` - Price per night
- `room.images[]` - Array of room images (same structure as package images)

#### Car Dealer Options (`day.car_dealers[]`)
Each car dealer object contains:
- `car_dealer.id` - Car dealer ID
- `car_dealer.name` - Car dealer name
- `car_dealer.contact_no` - Contact number
- `car_dealer.location` - Location object (same structure as hotel location)
- `car_dealer.images[]` - Array of car dealer images

#### Activities (`day.activities[]`)
Each activity object contains:
- `activity.name` - Activity name
- `activity.type` - Activity type (event, sightseeing, etc.)
- `activity.description` - Activity description
- `activity.charges` - Activity charges/price
- `activity.contact_no` - Contact number
- `activity.sequence` - Display sequence
- `activity.location` - Location object (same structure as hotel location)
- `activity.images[]` - Array of activity images
- `activity.itinerary_item_id` - Itinerary item ID

---

## 5. COMPANY PROFILE DATA (`company_profile`)

### Basic Company Info
- `company_profile.company_name` - Company name
- `company_profile.phone_number` - Primary phone
- `company_profile.alternate_phone` - Alternate phone
- `company_profile.email` - Company email
- `company_profile.website` - Company website

### Company Address (`company_profile.address`)
- `company_profile.address.line1` - Address line 1
- `company_profile.address.line2` - Address line 2
- `company_profile.address.city` - City
- `company_profile.address.state` - State
- `company_profile.address.country` - Country
- `company_profile.address.pincode` - Postal/ZIP code

### Company Images
- `company_profile.images.logo[]` - Array of logo images
- `company_profile.images.banner[]` - Array of banner images

Each image object contains:
- `image.id` - Image ID
- `image.image_url` - Absolute file path (converted for PDF)
- `image.description` - Image description

---

## 6. CREATED BY USER DATA (`created_by`)

- `created_by.id` - User ID
- `created_by.name` - Full name
- `created_by.first_name` - First name (split from full name)
- `created_by.last_name` - Last name (split from full name)
- `created_by.username` - Username
- `created_by.email` - User email
- `created_by.mobileno` - User mobile number

---

## 7. METADATA

- `generated_date` - PDF generation date (formatted: "January 15, 2024")
- `generated_time` - PDF generation time (formatted: "02:30 PM")
- `base_dir` - Base directory path for file references

---

## USAGE IN HTML TEMPLATE

All fields can be accessed using Django template syntax:

```django
{# Basic fields #}
{{ package.name }}
{{ package.package_amount }}

{# Conditional rendering #}
{% if package.terms_and_conditions %}
    {{ package.terms_and_conditions }}
{% endif %}

{# Loops #}
{% for image in package.images %}
    <img src="{{ image.image_url }}" alt="{{ image.description }}">
{% endfor %}

{# Nested loops - Itinerary with hotels and rooms #}
{% for day in package.itinerary_details %}
    <h3>Day {{ day.day }}: {{ day.title }}</h3>
    
    {% for hotel in day.hotel_details %}
        <h4>{{ hotel.name }}</h4>
        
        {% for room in hotel.rooms %}
            <p>{{ room.name }} - ${{ room.price_per_night }}/night</p>
        {% endfor %}
    {% endfor %}
{% endfor %}
```

---

## NOTES

1. **All image URLs are converted to absolute file paths** for WeasyPrint compatibility
2. **All numeric fields** (prices, ratings) are converted to appropriate types
3. **Optional fields** may be None/null - always use `{% if %}` checks
4. **Arrays may be empty** - check with `{% if array %}` before looping
5. **Pricing is in decimal format** - use `{{ package.package_amount|floatformat:2 }}` for formatting

