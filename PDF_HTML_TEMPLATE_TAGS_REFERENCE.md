# Complete HTML Template Tags Reference for Lead PDF

## Table of Contents
1. [Lead Information](#1-lead-information)
2. [Customer Information](#2-customer-information)
3. [Package Basic Information](#3-package-basic-information)
4. [Package Pricing](#4-package-pricing)
5. [Package Images](#5-package-images)
6. [Package Inclusions](#6-package-inclusions)
7. [Package Exclusions](#7-package-exclusions)
8. [Package Amenities](#8-package-amenities)
9. [Package Policies](#9-package-policies)
10. [Terms and Conditions](#10-terms-and-conditions)
11. [Itinerary - Day Details](#11-itinerary---day-details)
12. [Itinerary - Hotel Details](#12-itinerary---hotel-details)
13. [Itinerary - Room Details](#13-itinerary---room-details)
14. [Itinerary - Transportation](#14-itinerary---transportation)
15. [Itinerary - Activities](#15-itinerary---activities)
16. [Company Profile](#16-company-profile)
17. [Created By User](#17-created-by-user)
18. [Metadata](#18-metadata)

---

## 1. Lead Information

```django
{# Lead ID #}
{{ lead.lead_id }}

{# Lead Status #}
{{ lead.status }}

{# Lead Created Date #}
{{ lead.created_at }}
```

---

## 2. Customer Information

```django
{# Customer Full Name #}
{{ customer.name }}

{# Customer First/Last Name #}
{{ customer.first_name }}
{{ customer.last_name }}

{# Customer Contact #}
{{ customer.email }}
{{ customer.mobileno }}

{# Customer Company (optional) #}
{% if customer.company %}
    {{ customer.company }}
{% endif %}

{# Customer Address (optional) #}
{% if customer.address %}
    {{ customer.address }}
{% endif %}
```

---

## 3. Package Basic Information

```django
{# Package Name #}
{{ package.name }}

{# Package Description #}
{{ package.description }}

{# Package Type #}
{{ package.type }}  {# family, couple, honeymoon, group #}

{# Number of People #}
{{ package.pax_size }}

{# Number of Days #}
{{ package.no_of_days }}

{# Transport Type #}
{{ package.transport_type }}

{# Contains Travel Fare #}
{% if package.contains_travel_fare %}
    Includes travel fare
{% else %}
    Travel fare not included
{% endif %}

{# Package Notes #}
{% if package.notes %}
    {{ package.notes }}
{% endif %}
```

---

## 4. Package Pricing

```django
{# Total Package Amount #}
{{ package.package_amount }}

{# Formatted with 2 decimals #}
${{ package.package_amount|floatformat:2 }}

{# Formatted with currency symbol #}
{% if package.package_amount %}
    Total: ${{ package.package_amount|floatformat:2 }}
{% endif %}
```

---

## 5. Package Images

```django
{# All Package Images #}
{% if package.images %}
    {% for image in package.images %}
        <img src="{{ image.image_url }}" alt="{{ image.description|default:'Package Image' }}">
        
        {# Image with description #}
        {% if image.description %}
            <p>{{ image.description }}</p>
        {% endif %}
    {% endfor %}
{% endif %}

{# First Package Image Only #}
{% if package.images %}
    {% for image in package.images %}
        {% if forloop.first %}
            <img src="{{ image.image_url }}" alt="{{ package.name }}">
        {% endif %}
    {% endfor %}
{% endif %}

{# Specific Image by Index #}
{% if package.images %}
    {% for image in package.images %}
        {% if forloop.counter == 2 %}  {# Second image #}
            <img src="{{ image.image_url }}" alt="Image {{ forloop.counter }}">
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## 6. Package Inclusions

```django
{# All Inclusions #}
{% if package.inclusions %}
    <h3>What's Included</h3>
    <ul>
    {% for inclusion in package.inclusions %}
        <li>
            <strong>{{ inclusion.name }}</strong>
            {% if inclusion.description %}
                - {{ inclusion.description }}
            {% endif %}
        </li>
    {% endfor %}
    </ul>
{% endif %}

{# Inclusions Count #}
{% if package.inclusions %}
    {{ package.inclusions|length }} inclusions
{% endif %}
```

---

## 7. Package Exclusions

```django
{# All Exclusions #}
{% if package.exclusions %}
    <h3>What's Not Included</h3>
    <ul>
    {% for exclusion in package.exclusions %}
        <li>
            <strong>{{ exclusion.name }}</strong>
            {% if exclusion.description %}
                - {{ exclusion.description }}
            {% endif %}
        </li>
    {% endfor %}
    </ul>
{% endif %}
```

---

## 8. Package Amenities

```django
{# All Amenities #}
{% if package.amenities %}
    <h3>Amenities</h3>
    <ul>
    {% for amenity in package.amenities %}
        <li>
            <strong>{{ amenity.name }}</strong>
            {% if amenity.description %}
                - {{ amenity.description }}
            {% endif %}
        </li>
    {% endfor %}
    </ul>
{% endif %}
```

---

## 9. Package Policies

```django
{# All Policies #}
{% if package.policies %}
    <h3>Policies</h3>
    {% for policy in package.policies %}
        <div class="policy">
            <h4>{{ policy.name }}</h4>
            {% if policy.description %}
                <p>{{ policy.description }}</p>
            {% endif %}
        </div>
    {% endfor %}
{% endif %}
```

---

## 10. Terms and Conditions

```django
{# Terms and Conditions #}
{% if package.terms_and_conditions %}
    <h3>Terms & Conditions</h3>
    <div class="terms">
        {{ package.terms_and_conditions|linebreaks }}
    </div>
{% endif %}

{# Or as raw HTML if it contains HTML tags #}
{% if package.terms_and_conditions %}
    <h3>Terms & Conditions</h3>
    <div class="terms">
        {{ package.terms_and_conditions|safe }}
    </div>
{% endif %}
```

---

## 11. Itinerary - Day Details

```django
{# All Days in Itinerary #}
{% if package.itinerary_details %}
    {% for day in package.itinerary_details %}
        <div class="day-section">
            {# Day Number #}
            <h2>Day {{ day.day }}</h2>
            
            {# Day Title #}
            <h3>{{ day.title }}</h3>
            
            {# Location #}
            <p>{{ day.city }}{% if day.state %}, {{ day.state }}{% endif %}</p>
            
            {# Day Description #}
            {% if day.description %}
                <p>{{ day.description }}</p>
            {% endif %}
            
            {# Day Note #}
            {% if day.note %}
                <div class="note">{{ day.note }}</div>
            {% endif %}
        </div>
    {% endfor %}
{% endif %}
```

---

## 12. Itinerary - Hotel Details

```django
{# Hotels for Each Day #}
{% for day in package.itinerary_details %}
    <h2>Day {{ day.day }}: {{ day.title }}</h2>
    
    {# All Hotel Options for This Day #}
    {% if day.hotel_details %}
        <h3>Hotel Options</h3>
        {% for hotel in day.hotel_details %}
            <div class="hotel-card">
                {# Hotel Name #}
                <h4>{{ hotel.name }}</h4>
                
                {# Hotel Rating #}
                {% if hotel.rating %}
                    <p>Rating: {{ hotel.rating }}/5</p>
                {% endif %}
                
                {# Hotel Description #}
                {% if hotel.description %}
                    <p>{{ hotel.description }}</p>
                {% endif %}
                
                {# Hotel Location #}
                {% if hotel.location %}
                    <p>
                        {% if hotel.location.address %}{{ hotel.location.address }}, {% endif %}
                        {{ hotel.location.city }}, {{ hotel.location.state }}, {{ hotel.location.country }}
                    </p>
                {% endif %}
                
                {# Hotel Contact #}
                {% if hotel.phoneno %}
                    <p>Phone: {{ hotel.phoneno }}</p>
                {% endif %}
                {% if hotel.website %}
                    <p>Website: {{ hotel.website }}</p>
                {% endif %}
                
                {# Hotel Images #}
                {% if hotel.images %}
                    <div class="hotel-images">
                        {% for image in hotel.images %}
                            <img src="{{ image.image_url }}" alt="{{ hotel.name }}">
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    {% endif %}
{% endfor %}
```

---

## 13. Itinerary - Room Details

```django
{# Rooms for Each Hotel #}
{% for day in package.itinerary_details %}
    {% for hotel in day.hotel_details %}
        <h4>{{ hotel.name }} - Room Options</h4>

        {% if hotel.rooms %}
            <div class="rooms-grid">
                {% for room in hotel.rooms %}
                    <div class="room-card">
                        {# Room Name #}
                        <h5>{{ room.name }}</h5>

                        {# Room Type #}
                        <p>Type: {{ room.type|title }}</p>

                        {# Room Capacity #}
                        {% if room.capacity %}
                            <p>Capacity: {{ room.capacity }} person{% if room.capacity > 1 %}s{% endif %}</p>
                        {% endif %}

                        {# Bed Type #}
                        {% if room.bedtype %}
                            <p>Bed: {{ room.bedtype|title }}</p>
                        {% endif %}

                        {# Room Description #}
                        {% if room.description %}
                            <p>{{ room.description }}</p>
                        {% endif %}

                        {# Room Rating #}
                        {% if room.rating %}
                            <p>Rating: {{ room.rating }}/5</p>
                        {% endif %}

                        {# Price Per Night #}
                        {% if room.price_per_night %}
                            <p class="price">${{ room.price_per_night }}/night</p>
                        {% endif %}

                        {# Room Images #}
                        {% if room.images %}
                            <div class="room-images">
                                {% for image in room.images %}
                                    <img src="{{ image.image_url }}" alt="{{ room.name }}">
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endfor %}
{% endfor %}
```

---

## 14. Itinerary - Transportation

```django
{# Car Dealers/Transportation for Each Day #}
{% for day in package.itinerary_details %}
    <h2>Day {{ day.day }}: Transportation</h2>

    {% if day.car_dealers %}
        <h3>Transportation Options</h3>
        {% for car_dealer in day.car_dealers %}
            <div class="transport-card">
                {# Car Dealer Name #}
                <h4>{{ car_dealer.name }}</h4>

                {# Contact Number #}
                {% if car_dealer.contact_no %}
                    <p>Contact: {{ car_dealer.contact_no }}</p>
                {% endif %}

                {# Location #}
                {% if car_dealer.location %}
                    <p>
                        {{ car_dealer.location.city }}{% if car_dealer.location.state %}, {{ car_dealer.location.state }}{% endif %}
                    </p>
                {% endif %}

                {# Car Dealer Images #}
                {% if car_dealer.images %}
                    <div class="transport-images">
                        {% for image in car_dealer.images %}
                            <img src="{{ image.image_url }}" alt="{{ car_dealer.name }}">
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    {% endif %}
{% endfor %}
```

---

## 15. Itinerary - Activities

```django
{# Activities for Each Day #}
{% for day in package.itinerary_details %}
    <h2>Day {{ day.day }}: Activities</h2>

    {% if day.activities %}
        <h3>Planned Activities</h3>
        {% for activity in day.activities %}
            <div class="activity-card">
                {# Activity Name #}
                <h4>{{ activity.name }}</h4>

                {# Activity Type #}
                <p>Type: {{ activity.type|title }}</p>

                {# Activity Description #}
                {% if activity.description %}
                    <p>{{ activity.description }}</p>
                {% endif %}

                {# Activity Charges #}
                {% if activity.charges %}
                    <p class="price">Cost: ${{ activity.charges|floatformat:2 }}</p>
                {% endif %}

                {# Contact Number #}
                {% if activity.contact_no %}
                    <p>Contact: {{ activity.contact_no }}</p>
                {% endif %}

                {# Location #}
                {% if activity.location %}
                    <p>
                        Location: {{ activity.location.city }}{% if activity.location.state %}, {{ activity.location.state }}{% endif %}
                    </p>
                {% endif %}

                {# Activity Images #}
                {% if activity.images %}
                    <div class="activity-images">
                        {% for image in activity.images %}
                            <img src="{{ image.image_url }}" alt="{{ activity.name }}">
                        {% endfor %}
                    </div>
                {% endif %}

                {# Sequence Number #}
                {% if activity.sequence %}
                    <p>Order: {{ activity.sequence }}</p>
                {% endif %}
            </div>
        {% endfor %}
    {% endif %}
{% endfor %}
```

---

## 16. Company Profile

```django
{# Company Name #}
{{ company_profile.company_name }}

{# Company Contact #}
{{ company_profile.phone_number }}
{% if company_profile.alternate_phone %}
    {{ company_profile.alternate_phone }}
{% endif %}
{{ company_profile.email }}

{# Company Website #}
{% if company_profile.website %}
    {{ company_profile.website }}
{% endif %}

{# Company Address #}
{% if company_profile.address %}
    <address>
        {% if company_profile.address.line1 %}{{ company_profile.address.line1 }}<br>{% endif %}
        {% if company_profile.address.line2 %}{{ company_profile.address.line2 }}<br>{% endif %}
        {{ company_profile.address.city }}, {{ company_profile.address.state }}<br>
        {{ company_profile.address.country }} - {{ company_profile.address.pincode }}
    </address>
{% endif %}

{# Company Logo #}
{% if company_profile.images.logo %}
    {% for logo in company_profile.images.logo %}
        {% if forloop.first %}
            <img src="{{ logo.image_url }}" alt="{{ company_profile.company_name }}" class="logo">
        {% endif %}
    {% endfor %}
{% endif %}

{# Company Banner #}
{% if company_profile.images.banner %}
    {% for banner in company_profile.images.banner %}
        {% if forloop.first %}
            <img src="{{ banner.image_url }}" alt="Banner" class="banner">
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## 17. Created By User

```django
{# User Full Name #}
{{ created_by.name }}

{# User First/Last Name #}
{{ created_by.first_name }} {{ created_by.last_name }}

{# User Contact #}
{{ created_by.email }}
{{ created_by.mobileno }}

{# Username #}
{{ created_by.username }}
```

---

## 18. Metadata

```django
{# Generated Date #}
{{ generated_date }}  {# e.g., "January 15, 2024" #}

{# Generated Time #}
{{ generated_time }}  {# e.g., "02:30 PM" #}

{# Base Directory (for file paths) #}
{{ base_dir }}
```

---

## SUMMARY OF ALL AVAILABLE TEMPLATE TAGS

### Lead
- `{{ lead.lead_id }}`, `{{ lead.status }}`, `{{ lead.created_at }}`

### Customer
- `{{ customer.name }}`, `{{ customer.first_name }}`, `{{ customer.last_name }}`
- `{{ customer.email }}`, `{{ customer.mobileno }}`
- `{{ customer.company }}`, `{{ customer.address }}`

### Package Basic
- `{{ package.name }}`, `{{ package.description }}`, `{{ package.type }}`
- `{{ package.pax_size }}`, `{{ package.no_of_days }}`
- `{{ package.package_amount }}`
- `{{ package.transport_type }}`, `{{ package.contains_travel_fare }}`
- `{{ package.terms_and_conditions }}`, `{{ package.notes }}`

### Package Arrays (use {% for %})
- `package.images[]` - All package images
- `package.inclusions[]` - What's included
- `package.exclusions[]` - What's not included
- `package.amenities[]` - Package amenities
- `package.policies[]` - Package policies
- `package.itinerary_details[]` - Day-wise itinerary

### Itinerary Structure (nested loops)
- `day.day`, `day.title`, `day.description`, `day.city`, `day.state`, `day.note`
- `day.hotel_details[]` → Multiple hotel options per day
  - `hotel.name`, `hotel.rating`, `hotel.description`, `hotel.phoneno`, `hotel.website`
  - `hotel.location.city`, `hotel.location.state`, `hotel.location.country`, `hotel.location.address`
  - `hotel.images[]` → Hotel images
  - `hotel.rooms[]` → Room options
    - `room.name`, `room.type`, `room.capacity`, `room.bedtype`
    - `room.description`, `room.rating`, `room.price_per_night`
    - `room.images[]` → Room images
- `day.car_dealers[]` → Transportation options
  - `car_dealer.name`, `car_dealer.contact_no`
  - `car_dealer.location`, `car_dealer.images[]`
- `day.activities[]` → Activities for the day
  - `activity.name`, `activity.type`, `activity.description`
  - `activity.charges`, `activity.contact_no`, `activity.sequence`
  - `activity.location`, `activity.images[]`

### Company Profile
- `{{ company_profile.company_name }}`
- `{{ company_profile.phone_number }}`, `{{ company_profile.alternate_phone }}`, `{{ company_profile.email }}`, `{{ company_profile.website }}`
- `{{ company_profile.address.line1 }}`, `{{ company_profile.address.line2 }}`, `{{ company_profile.address.city }}`, `{{ company_profile.address.state }}`, `{{ company_profile.address.country }}`, `{{ company_profile.address.pincode }}`
- `company_profile.images.logo[]`, `company_profile.images.banner[]`

### Created By User
- `{{ created_by.name }}`, `{{ created_by.first_name }}`, `{{ created_by.last_name }}`
- `{{ created_by.email }}`, `{{ created_by.mobileno }}`, `{{ created_by.username }}`

### Metadata
- `{{ generated_date }}`, `{{ generated_time }}`, `{{ base_dir }}`

---

## IMPORTANT NOTES

1. **All image URLs are already converted to absolute file paths** - just use `{{ image.image_url }}`
2. **Always check if data exists** before displaying: `{% if field %}...{% endif %}`
3. **Use filters for formatting**:
   - `|floatformat:2` - Format decimals
   - `|title` - Capitalize words
   - `|linebreaks` - Convert line breaks to HTML
   - `|safe` - Render HTML without escaping
4. **Loop helpers**:
   - `forloop.first`, `forloop.last`, `forloop.counter`
5. **Array length**: `{{ array|length }}`
6. **Default values**: `{{ field|default:"Not specified" }}`

