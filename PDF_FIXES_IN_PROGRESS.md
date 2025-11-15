# PDF Template Fixes - In Progress

## Issues Reported by User

1. **Font sizes are incorrect** - Need to rollback to old font sizes
2. **About Us section** - Address showing as JSON, yellow highlight on company name
3. **Your Agent section** - Need vector image on left side
4. **Itinerary section** - Need to show ALL details (hotels, room types, pictures, offerings, etc.)

## Fixes Completed ✅

### 1. About Us Section - Fixed
- ✅ **Removed yellow highlight** - Changed from `<span class="highlight">` to `<strong>`
- ✅ **Fixed address parsing** - Now properly parses address object:
  ```django
  {% if company_profile.address.line1 %}{{ company_profile.address.line1 }}{% endif %}
  {% if company_profile.address.line2 %}, {{ company_profile.address.line2 }}{% endif %}
  {% if company_profile.address.city %}, {{ company_profile.address.city }}{% endif %}
  {% if company_profile.address.state %}, {{ company_profile.address.state }}{% endif %}
  {% if company_profile.address.country %}, {{ company_profile.address.country }}{% endif %}
  {% if company_profile.address.pincode %} - {{ company_profile.address.pincode }}{% endif %}
  ```

### 2. Your Agent Section - Fixed
- ✅ **Added vector image** - Created SVG curve image at `media/images/agent_vector.svg`
- ✅ **Removed yellow highlights** - Changed from `.highlight` class to `<strong>` tags
- ✅ **Updated CSS** - Changed `.agent-circle` to `.agent-vector` class
- ✅ **Passed base_dir to template** - Added `base_dir` to context in `pdf_generator.py`

### 3. Font Sizes - Partially Fixed
- ✅ **Cover title** - Rolled back from 90pt to 48pt
- ✅ **Badge labels/values** - Rolled back from 20pt to 11pt
- ✅ **About content** - Rolled back from 20pt to 11pt
- ✅ **Services list** - Rolled back from 20pt to 11pt
- ✅ **Agent description** - Rolled back from 20pt to 10pt
- ⏳ **Still need to rollback** - Many other sections still at 90pt/20pt

## Fixes Still Needed ⏳

### Font Sizes to Rollback

**Headers (currently 90pt, should be smaller):**
- `.agent-title` - 90pt → 64pt
- `.customers-title` - 90pt → 56pt
- `.testimonials-title` - 90pt → 56pt
- `.trip-title` - 90pt → 56pt
- `.day-page-title` - 90pt → 56pt
- `.addons-title` - 90pt → 48pt
- `.approval-title` - 90pt → 56pt

**Body text (currently 20pt, should be smaller):**
- `.agent-intro` - 20pt → 11pt ✅ (done)
- `.customers-intro` - 20pt → 10pt
- `.testimonial-name` - 20pt → 14pt
- `.testimonial-text` - 20pt → 9pt
- `.trip-content` - 20pt → 10pt
- `.day-text` - 20pt → 11pt
- `.addons-intro` - 20pt → 11pt
- `.addon-title` - 20pt → 14pt
- `.addon-text` - 20pt → 9pt
- `.approval-content` - 20pt → 11pt
- `.approval-thank-you` - 20pt → 18pt
- `.signature-icon` - 20pt → 14pt
- `.signature-line` - 20pt → 10pt
- `.client-approval` - 20pt → 10pt
- `.itinerary-day-number` - 20pt → 14pt
- `.itinerary-day-title` - 20pt → 16pt
- `.itinerary-day-content` - 20pt → 10pt
- `.itinerary-hotel-name` - 20pt → 11pt

### Itinerary Expansion

**Current State:**
- Shows basic day information
- Limited hotel details
- No room types, offerings, or multiple hotel options

**Needed:**
- Show ALL hotel options for each day
- Display room types with details (capacity, bed type, price)
- Show hotel images
- Display hotel offerings/amenities
- Show transportation options
- Include all activity details with images

**Data Structure Available:**
```json
{
  "itinerary_details": [
    {
      "day": 1,
      "title": "Arrival",
      "description": "...",
      "hotel_details": [  // Multiple options
        {
          "id": 1,
          "name": "Hotel A",
          "location": {...},
          "rating": 4.5,
          "images": [...],
          "rooms": [  // Room types
            {
              "id": 1,
              "type": "deluxe",
              "capacity": 2,
              "bedtype": "king",
              "price_per_night": "150",
              "description": "...",
              "images": [...]
            }
          ]
        }
      ],
      "car_dealer_details": [...],
      "activities": [...]
    }
  ]
}
```

## Files Modified

1. **`tour_management/templates/lead_pdf_template.html`**
   - Fixed About Us address parsing
   - Removed yellow highlights
   - Added vector image support
   - Partially rolled back font sizes

2. **`tour_management/utils/pdf_generator.py`**
   - Added `base_dir` to template context

3. **`media/images/agent_vector.svg`** (NEW)
   - Created SVG curve vector image

## Next Steps

1. **Complete font size rollback** - Update remaining 90pt/20pt sizes
2. **Expand itinerary section** - Show all hotel details, room types, images
3. **Test PDF generation** - Verify all changes work correctly
4. **Adjust styling** - Fine-tune appearance as needed

## Testing Command

```bash
curl -X POST http://localhost:8000/lead/generate_pdf/ \
  -H "Content-Type: application/json" \
  -d '{"lead_id": YOUR_LEAD_ID}'
```

## Notes

- Font family is now consistently Poppins throughout
- Yellow highlights (#FFF9C4) have been removed
- Address is properly parsed from JSON object
- Vector image path uses `file://{{ base_dir }}/media/images/agent_vector.svg`

