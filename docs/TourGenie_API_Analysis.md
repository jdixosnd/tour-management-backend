# TourGenie API Analysis

## Overview
This document outlines the analysis of the network requests made by the TourGenie website to fetch tour package details.

**Target URL:** `https://tourgenie.com/leisure/north-bengal-tour-packages/getaway-to-jaldapara`

## API Details

Based on the analysis of the application's JavaScript bundles, the following API details were identified.

### Base URL
`https://tg.api.tourgenie.com/api`

### Discovery Flow (How to reach the package)

To programmatically find the target URL `.../getaway-to-jaldapara`, the application follows a discovery process starting from categories.

#### 1. Get Categories
**Endpoint:** `/activityandblogcategory/getactivityandblogcategory`
**Method:** `GET`
**Description:** Fetches all available activity and blog categories to find the "Leisure" category ID.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/activityandblogcategory/getactivityandblogcategory"
```

**Response Snippet:**
```json
[
    {
        "activity_and_blog_category_id": 7,
        "activity_and_blog_category": "Leisure",
        ...
    }
]
```
*We identify that "Leisure" corresponds to ID `7`.*

#### 2. Get Holiday List (Filtered)
**Endpoint:** `/Itinerary/GetHolidayList`
**Method:** `POST`
**Description:** Fetches a list of holiday packages filtered by the category ID.

**Example Request:**
```bash
curl -X POST "https://tg.api.tourgenie.com/api/Itinerary/GetHolidayList" \
     -H "Content-Type: application/json" \
     -d '{"budget_min_value":0,"budget_max_value":100000,"package_category_id":"7"}'
```

**Key Response Fields:**
The response is a list of packages. We look for the one matching our target.
```json
[
  {
    "itinerary_id": 150,
    "itinerary_name": "Getaway to Jaldapara",
    "url_slug": "getaway-to-jaldapara",
    ...
  }
]
```
*The `url_slug` field ("getaway-to-jaldapara") is then used to call the details endpoints documented below.*

### Package Details Endpoints

There are two endpoints that can be used to fetch the details of a holiday package using its slug (URL part). The application uses these to retrieve SEO metadata and package details.

#### 1. Get Details by Holiday Name (Slug)
**Endpoint:** `/Itinerary/GetHolidayDetailsByHolidayName/{slug}`
**Method:** `GET`
**Description:** Fetches the full details of the holiday package.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/Itinerary/GetHolidayDetailsByHolidayName/getaway-to-jaldapara"
```

#### 2. Get Details by URL Slug
**Endpoint:** `/Itinerary/GetHolidayDetailsByUrlSlug/{slug}`
**Method:** `GET`
**Description:** Fetches details, primarily used for SEO purposes (meta tags) in the application initialization, but returns the same data structure as above.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/Itinerary/GetHolidayDetailsByUrlSlug/getaway-to-jaldapara"
```

#### 3. Get Price Details
**Endpoint:** `/Itinerary/GetHolidayView_ItineraryPrice/{itinerary_id}/{price_id}`
**Method:** `GET`
**Description:** Fetches specific price breakdown for a given itinerary and price ID.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/Itinerary/GetHolidayView_ItineraryPrice/150/109"
```

#### 4. Get Inclusions
**Endpoint:** `/Itinerary/GetItinerary_InclusionsExclusions_by_ItineraryId/{itinerary_id}/inclusions`
**Method:** `GET`
**Description:** Fetches the inclusion details (HTML format) for the itinerary.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/Itinerary/GetItinerary_InclusionsExclusions_by_ItineraryId/150/inclusions"
```

#### 5. Get Exclusions
**Endpoint:** `/Itinerary/GetItinerary_InclusionsExclusions_by_ItineraryId/{itinerary_id}/exclusions`
**Method:** `GET`
**Description:** Fetches the exclusion details (HTML format) for the itinerary.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/Itinerary/GetItinerary_InclusionsExclusions_by_ItineraryId/150/exclusions"
```

#### 6. Get Day-wise Itinerary
**Endpoint:** `/Itinerary/GetHolidayView_Itinerary/{itinerary_id}`
**Method:** `GET`
**Description:** Fetches the day-wise details of the itinerary, including activities, accommodation, and transfers for each day.

**Example Request:**
```bash
curl "https://tg.api.tourgenie.com/api/Itinerary/GetHolidayView_Itinerary/150"
```

---

## Response Structure

The response is a JSON array containing a single object with the package details.

**Sample Response (Formatted):**
```json
[
  {
    "itinerary_id": 150,
    "itinerary_name": "Getaway to Jaldapara",
    "itinerary_description": "Getaway to Jaldapara: explore forests, visit Chilapata, enjoy elephant and jeep safaris with our exclusive Darjeeling Tour Package.",
    "duration_in_days": 3,
    "adult": 2,
    "child": 0,
    "infant": 0,
    "start_date": null,
    "end_date": null,
    "images_desktop": "{\"images\":[\"assets\\\\CRM\\\\Itinerary\\\\150\\\\Desktop\\\\55d567a6-a37a-446b-8607-b5f3de398c2d.png\",\"...\"],\"desktopCoverIndex\":0}",
    "images_mobile": null,
    "meta_title_tag": "Getaway to Jaldapara – North Bengal Tour Packages | Wildlife & Nature",
    "meta_keywords": "Jaldapara tour packages, North Bengal travel, Jaldapara wildlife sanctuary, Dooars holidays, jungle safari, nature escape, getaway to Jaldapara, North Bengal tour",
    "meta_description": "Explore our exclusive Jaldapara tour packages in North Bengal. Perfect for wildlife lovers and nature enthusiasts. Includes jungle safari, scenic stays & more.",
    "image_alt": null,
    "user_rating": 4.3,
    "user_rating_string": "Excellent",
    "destination_name_from": "Siliguri",
    "state_id": 13,
    "state_name": "North Bengal",
    "state_id_to": 13,
    "state_name_to": "North Bengal",
    "destination_name_to": "Alipurduar",
    "itinerary_price_id": 109,
    "from_date": "2024-09-01T00:00:00",
    "to_date": "2025-12-31T00:00:00",
    "traveller_total": 6756.75,
    "service_provider_total": 6468.00,
    "corporate_total": 6352.50,
    "base_price": 5500.00,
    "base_price_divided_by_two": 2750.00,
    "holiday_offer_transfer": 0,
    "holiday_offer_activity": 0,
    "holiday_offer_accommodation": 0,
    "total_count": 1
  }
]
```

**Price Details Sample Response:**
```json
[
  {
    "itinerary_name": "Getaway to Jaldapara",
    "itinerary_description": "Getaway to Jaldapara: explore forests, visit Chilapata, enjoy elephant and jeep safaris with our exclusive Darjeeling Tour Package.",
    "adult": 2,
    "child": 0,
    "infant": 0,
    "child_age_range": null,
    "infant_age_range": null,
    "traveller_total": 6756.75,
    "service_provider_total": 6468.00,
    "corporate_total": 6352.50,
    "base_price": 5500.00,
    "base_price_divided_by_adult": 2750.00,
    "base_rate_plus_traveler_markup": 3217.50,
    "gst": 5.00,
    "traveller_gst_price": 337.837500,
    "total_guest_excluding_infant": 2
  }
]
  }
]
```

**Day-wise Itinerary Sample Response:**
```json
[
  {
    "itinerary_id": 150,
    "itinerary_day": 1,
    "itinerary_title": "Arrival Bagdogra - Jaldapara",
    "itinerary_description": "Welcome on arrival at IXB/NJP ...",
    "day_destination": "Alipurduar",
    "transfer": [],
    "accommodation": [],
    "activity": []
  }
]
```

### Key Fields Table

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `itinerary_id` | Number | Unique identifier for the itinerary. |
| `itinerary_name` | String | Name of the tour package. |
| `duration_in_days` | Number | Duration of the tour in days. |
| `images_desktop` | JSON String | Contains a list of image paths (relative to `IMAGE_API_URL` which is `https://tg.api.tourgenie.com/`). |
| `traveller_total` | Number | Total price for the traveler. |
| `user_rating` | Number | Average user rating. |
| `meta_title_tag` | String | SEO Title tag. |
| `meta_description`| String | SEO Description. |

## Notes
## Image URL Construction

The application stores image paths as JSON strings within various fields. To construct the fully qualified URL:

1.  **Base URL:** All images are hosted at `https://tg.api.tourgenie.com/`.
2.  **Parsing:** The field value (e.g., `images_desktop`, `activity_image`) is a JSON string. Parse this string to parse the relative path.
3.  **Concatenation:** Append the parsed relative path to the Base URL.

### Logic by Type

The parsing logic depends on the entity type (derived from client-side code analysis):

*   **Packages / Stays:**
    *   Parse the JSON to get an object.
    *   Find the `images` array and the `desktopCoverIndex` (or similar index field).
    *   Select the image at the specified index.
    *   **Fields:** `images_desktop`, `stay_image`.
    *   **Example Path:** `assets/CRM/Itinerary/150/Desktop/image.png`

*   **Activities:**
    *   Parse the JSON.
    *   Use `cover_image_index` to select from `image_paths`.
    *   **Fields:** `activity_image`.
    *   **Example Path:** `assets/CRM/Activity/Desktop/40/Sing_....webp`

*   **Transfers:**
    *   Parse the JSON.
    *   The result might be the path string directly or an array where the first element is the path.
    *   **Fields:** `transfer_image`.

**Example:**
If `activity_image` contains `{"image_paths":["assets/CRM/Activity/Desktop/40/Sing.webp"], "cover_image_index":0}`, the full URL is:
`https://tg.api.tourgenie.com/assets/CRM/Activity/Desktop/40/Sing.webp`

## Notes
## Stays API

The application also exposes an API to fetch a list of stays (hotels, homestays, etc.) with filtering options.

#### 1. Get Stay List
**Endpoint:** `/Stay/GetStayList`
**Method:** `POST`
**Description:** Fetches a list of stays filtered by budget and potentially other criteria.

**Example Request:**
```bash
curl -X POST "https://tg.api.tourgenie.com/api/Stay/GetStayList" \
     -H "Content-Type: application/json" \
     -d '{"budget_min_value":0,"budget_max_value":100000}'
```

**Sample Response:**
```json
[
  {
    "stay_id": 278,
    "stay_name": "Clover homestay",
    "stay_description": "The Property is located in Dimapur...",
    "stay_category": 3,
    "stay_rating": 5.0,
    "checkin_time": "17:00",
    "checkout_time": "11:00",
    "stay_type_id": 6,
    "stay_type_name": "Homestays",
    "destination_id": 295,
    "destination_name": "Dimapur",
    "state_id": 9,
    "state_name": "Nagaland",
    "phone": "+91 7384718607",
    "email": "booking@tourgenie.com",
    "address": "Near Co-Operative, Middle Sichey Gangtok, East Sikkim, India, 737101",
    "images_desktop": "{\"images\":[\"assets\\\\CRM\\\\Stay\\\\278\\\\Desktop\\\\cropped-image_71da5dd0-6bf9-4a6f-8664-9041ad060dbe.png\",...],\"desktopCoverIndex\":0}",
    "url_slug": "clover-homestay",
    "base_rate": 1800.00,
    "count_amenities": 8,
    "base_rate_plus_traveler_markup": 2106.00,
    "meal_plan_name": "No meals included",
    "stay_room_type_name": "Double Room",
    "traveller_tax": 324.00,
    "total_count": 40
  },
  ...
]
```
