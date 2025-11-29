# Travel Dates Feature - Lead and Booking APIs

## 📋 Overview

Travel start and end dates have been added to both **Lead** and **Booking (Transaction)** models. This allows tour operators to track when customers plan to travel.

### What Changed?

- ✅ **Added**: `travel_start_date` and `travel_end_date` fields to Lead model
- ✅ **Updated**: Lead creation API to accept travel dates
- ✅ **Updated**: Lead update API to allow updating travel dates
- ✅ **Updated**: Lead get APIs to return travel dates
- ✅ **Updated**: Booking creation API to copy travel dates from lead or accept new dates
- ✅ **Updated**: Booking update API already supported travel dates (no changes needed)

---

## 🗄️ Database Changes

### Migration: `0017_auto_20251127_1413.py`

**Lead Table** - Added fields:
- `travel_start_date` (DATE, nullable)
- `travel_end_date` (DATE, nullable)

**Transaction Table** - Already had these fields:
- `travel_start_date` (DATE, nullable)
- `travel_end_date` (DATE, nullable)

---

## 📝 Lead APIs

### 1. Create Lead (`POST /lead/add/`)

#### Request Structure
```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "customer_id": 5,
  "status": "New",
  "travel_start_date": "2024-03-01",  // ✅ NEW - Optional
  "travel_end_date": "2024-03-05",    // ✅ NEW - Optional
  "package_snapshot": {
    "name": "Kerala Delight",
    "destination_id": 5,
    "no_of_days": 5,
    "package_amount": 50000,
    "package_options": [...]
  }
}
```

#### Response
```json
{
  "message": "Lead created successfully",
  "lead_id": 10,
  "lead_package_id": 15
}
```

---

### 2. Get Lead (`POST /lead/get/`)

#### Request
```json
{
  "lead_id": 10
}
```

#### Response
```json
{
  "lead_id": 10,
  "customer": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210"
  },
  "status": "New",
  "created_at": "2024-01-15T10:30:00Z",
  "travel_start_date": "2024-03-01",  // ✅ NEW
  "travel_end_date": "2024-03-05",    // ✅ NEW
  "package": {
    "id": 15,
    "name": "Kerala Delight",
    "package_options": [...]
  }
}
```

---

### 3. Get All Leads (`POST /lead/get_all/`)

#### Request
```json
{
  "tour_operator_id": 1,
  "page": 1,
  "page_size": 10
}
```

#### Response
```json
{
  "count": 25,
  "total_pages": 3,
  "current_page": 1,
  "leads": [
    {
      "lead_id": 10,
      "status": "New",
      "created_at": "2024-01-15T10:30:00Z",
      "travel_start_date": "2024-03-01",  // ✅ NEW
      "travel_end_date": "2024-03-05",    // ✅ NEW
      "customer": {...},
      "package": {...}
    }
  ]
}
```

---

### 4. Update Lead (`POST /lead/update/`)

#### Request Structure
```json
{
  "lead_id": 10,
  "created_by": 1,
  "status": "Follow-up",              // Optional
  "travel_start_date": "2024-03-10",  // ✅ NEW - Optional
  "travel_end_date": "2024-03-15",    // ✅ NEW - Optional
  "package_snapshot": {
    "name": "Updated Kerala Delight",
    "package_options": [...]
  }
}
```

#### Response
```json
{
  "message": "Lead updated successfully",
  "lead_id": 10
}
```

---

## 🎫 Booking (Transaction) APIs

### 1. Create Booking (`POST /booking/add/`)

**Behavior**: 
- If `travel_start_date` and `travel_end_date` are provided in the request, they will be used
- If NOT provided, the dates will be **copied from the lead**
- This allows flexibility to either use the lead's dates or override them during booking

#### Request Structure
```json
{
  "lead_id": 10,
  "created_by": 1,
  "travel_start_date": "2024-03-01",  // Optional - uses lead's date if not provided
  "travel_end_date": "2024-03-05",    // Optional - uses lead's date if not provided
  "itinerary_selections": [...],
  "base_amount": 45000,
  "final_amount": 45250
}
```


