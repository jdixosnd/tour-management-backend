# Quick Reference: All Available Template Tags

## 🎯 MOST COMMONLY NEEDED TAGS

### Pricing
```django
{{ package.package_amount }}              {# Total package price #}
{{ room.price_per_night }}                {# Room price per night #}
{{ activity.charges }}                    {# Activity cost #}
```

### Terms & Conditions
```django
{{ package.terms_and_conditions }}        {# Full T&C text #}
```

### Images
```django
{% for image in package.images %}         {# Package images #}
{% for image in hotel.images %}           {# Hotel images #}
{% for image in room.images %}            {# Room images #}
{% for image in activity.images %}        {# Activity images #}
```

### Inclusions & Exclusions
```django
{% for inclusion in package.inclusions %} {# What's included #}
{% for exclusion in package.exclusions %} {# What's not included #}
```

### Amenities & Policies
```django
{% for amenity in package.amenities %}    {# Package amenities #}
{% for policy in package.policies %}      {# Package policies #}
```

---

## 📦 COMPLETE TAG LIST

### Lead
```django
{{ lead.lead_id }}
{{ lead.status }}
{{ lead.created_at }}
```

### Customer
```django
{{ customer.name }}
{{ customer.first_name }}
{{ customer.last_name }}
{{ customer.email }}
{{ customer.mobileno }}
{{ customer.company }}
{{ customer.address }}
```

### Package - Basic
```django
{{ package.id }}
{{ package.name }}
{{ package.description }}
{{ package.type }}
{{ package.pax_size }}
{{ package.no_of_days }}
{{ package.package_amount }}
{{ package.contains_travel_fare }}
{{ package.transport_type }}
{{ package.destination_id }}
{{ package.notes }}
{{ package.terms_and_conditions }}
```

### Package - Arrays
```django
{% for image in package.images %}
    {{ image.id }}
    {{ image.image_url }}
    {{ image.description }}
    {{ image.order }}
{% endfor %}

{% for inclusion in package.inclusions %}
    {{ inclusion.id }}
    {{ inclusion.name }}
    {{ inclusion.description }}
    {{ inclusion.type }}
{% endfor %}

{% for exclusion in package.exclusions %}
    {{ exclusion.id }}
    {{ exclusion.name }}
    {{ exclusion.description }}
    {{ exclusion.type }}
{% endfor %}

{% for amenity in package.amenities %}
    {{ amenity.id }}
    {{ amenity.name }}
    {{ amenity.description }}
    {{ amenity.type }}
{% endfor %}

{% for policy in package.policies %}
    {{ policy.id }}
    {{ policy.name }}
    {{ policy.description }}
    {{ policy.type }}
{% endfor %}
```

### Itinerary - Day
```django
{% for day in package.itinerary_details %}
    {{ day.day }}
    {{ day.city }}
    {{ day.state }}
    {{ day.title }}
    {{ day.description }}
    {{ day.note }}
{% endfor %}
```

### Itinerary - Hotels
```django
{% for day in package.itinerary_details %}
    {% for hotel in day.hotel_details %}
        {{ hotel.id }}
        {{ hotel.name }}
        {{ hotel.description }}
        {{ hotel.rating }}
        {{ hotel.website }}
        {{ hotel.phoneno }}
        {{ hotel.location.city }}
        {{ hotel.location.state }}
        {{ hotel.location.country }}
        {{ hotel.location.address }}
        
        {% for image in hotel.images %}
            {{ image.image_url }}
        {% endfor %}
    {% endfor %}
{% endfor %}
```

### Itinerary - Rooms
```django
{% for day in package.itinerary_details %}
    {% for hotel in day.hotel_details %}
        {% for room in hotel.rooms %}
            {{ room.id }}
            {{ room.name }}
            {{ room.type }}
            {{ room.capacity }}
            {{ room.bedtype }}
            {{ room.description }}
            {{ room.rating }}
            {{ room.price_per_night }}
            
            {% for image in room.images %}
                {{ image.image_url }}
            {% endfor %}
        {% endfor %}
    {% endfor %}
{% endfor %}
```

### Itinerary - Transportation
```django
{% for day in package.itinerary_details %}
    {% for car_dealer in day.car_dealers %}
        {{ car_dealer.id }}
        {{ car_dealer.name }}
        {{ car_dealer.contact_no }}
        {{ car_dealer.location.city }}
        {{ car_dealer.location.state }}
        
        {% for image in car_dealer.images %}
            {{ image.image_url }}
        {% endfor %}
    {% endfor %}
{% endfor %}
```

### Itinerary - Activities
```django
{% for day in package.itinerary_details %}
    {% for activity in day.activities %}
        {{ activity.name }}
        {{ activity.type }}
        {{ activity.description }}
        {{ activity.charges }}
        {{ activity.contact_no }}
        {{ activity.sequence }}
        {{ activity.location.city }}
        {{ activity.location.state }}
        {{ activity.itinerary_item_id }}
        
        {% for image in activity.images %}
            {{ image.image_url }}
        {% endfor %}
    {% endfor %}
{% endfor %}
```

### Company Profile
```django
{{ company_profile.company_name }}
{{ company_profile.phone_number }}
{{ company_profile.alternate_phone }}
{{ company_profile.email }}
{{ company_profile.website }}
{{ company_profile.address.line1 }}
{{ company_profile.address.line2 }}
{{ company_profile.address.city }}
{{ company_profile.address.state }}
{{ company_profile.address.country }}
{{ company_profile.address.pincode }}

{% for logo in company_profile.images.logo %}
    {{ logo.image_url }}
{% endfor %}

{% for banner in company_profile.images.banner %}
    {{ banner.image_url }}
{% endfor %}
```

### Created By
```django
{{ created_by.id }}
{{ created_by.name }}
{{ created_by.first_name }}
{{ created_by.last_name }}
{{ created_by.username }}
{{ created_by.email }}
{{ created_by.mobileno }}
```

### Metadata
```django
{{ generated_date }}
{{ generated_time }}
{{ base_dir }}
```

---

## 🔧 USEFUL FILTERS

```django
{{ price|floatformat:2 }}                 {# Format to 2 decimals #}
{{ text|linebreaks }}                     {# Convert line breaks to <br> #}
{{ text|safe }}                           {# Render HTML without escaping #}
{{ word|title }}                          {# Capitalize first letter #}
{{ array|length }}                        {# Get array length #}
{{ field|default:"Not specified" }}       {# Default value if empty #}
```

---

## 🔁 LOOP HELPERS

```django
{% for item in array %}
    {{ forloop.counter }}                 {# 1, 2, 3, ... #}
    {{ forloop.counter0 }}                {# 0, 1, 2, ... #}
    {{ forloop.first }}                   {# True on first iteration #}
    {{ forloop.last }}                    {# True on last iteration #}
{% endfor %}
```

---

## ✅ CONDITIONAL CHECKS

```django
{% if field %}                            {# Check if exists and not empty #}
{% if array %}                            {# Check if array has items #}
{% if value > 0 %}                        {# Numeric comparison #}
{% if text == "value" %}                  {# String comparison #}
```

---

## 📋 COMMON PATTERNS

### Display first image only
```django
{% if package.images %}
    {% for image in package.images %}
        {% if forloop.first %}
            <img src="{{ image.image_url }}" alt="{{ package.name }}">
        {% endif %}
    {% endfor %}
{% endif %}
```

### Display specific image by index
```django
{% for image in package.images %}
    {% if forloop.counter == 2 %}         {# Second image #}
        <img src="{{ image.image_url }}">
    {% endif %}
{% endfor %}
```

### Count items
```django
{{ package.inclusions|length }} inclusions
{{ package.images|length }} images
```

### Format address
```django
{% if company_profile.address %}
    {{ company_profile.address.line1 }}{% if company_profile.address.line2 %}, {{ company_profile.address.line2 }}{% endif %}, {{ company_profile.address.city }}, {{ company_profile.address.state }}, {{ company_profile.address.country }} - {{ company_profile.address.pincode }}
{% endif %}
```

---

## 🎨 COMPLETE EXAMPLE

```django
{# Itinerary page with everything #}
{% for day in package.itinerary_details %}
    <div class="page">
        <h1>Day {{ day.day }}: {{ day.title }}</h1>
        <h2>{{ day.city }}, {{ day.state }}</h2>
        <p>{{ day.description }}</p>
        
        {# Hotels #}
        {% for hotel in day.hotel_details %}
            <h3>{{ hotel.name }} ({{ hotel.rating }}/5)</h3>
            {% for image in hotel.images %}
                <img src="{{ image.image_url }}">
            {% endfor %}
            
            {# Rooms #}
            {% for room in hotel.rooms %}
                <div>{{ room.name }} - ${{ room.price_per_night }}/night</div>
            {% endfor %}
        {% endfor %}
        
        {# Activities #}
        {% for activity in day.activities %}
            <h4>{{ activity.name }}</h4>
            <p>{{ activity.description }} - ${{ activity.charges }}</p>
        {% endfor %}
    </div>
{% endfor %}
```

