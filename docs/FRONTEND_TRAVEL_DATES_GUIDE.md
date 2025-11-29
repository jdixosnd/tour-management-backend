# Frontend Guide: Travel Dates Feature

## 🎯 What Changed?

Travel dates (`travel_start_date` and `travel_end_date`) have been added to **Leads** and are now integrated with **Bookings**.

---

## 📝 Lead APIs - What You Need to Do

### 1. **Lead Creation Form** (`POST /lead/add/`)

**Add two optional date fields** to your lead creation form:

```javascript
// Add these fields to your lead creation form
const createLead = async (leadData) => {
  const payload = {
    tour_operator_id: 1,
    created_by: userId,
    customer_id: customerId,
    status: "New",
    
    // ✅ NEW - Add these optional fields
    travel_start_date: "2024-03-01",  // Format: YYYY-MM-DD (optional)
    travel_end_date: "2024-03-05",    // Format: YYYY-MM-DD (optional)
    
    package_snapshot: {
      // ... existing package data
    }
  };

  const response = await fetch('/lead/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  return await response.json();
};
```

**UI Example:**
```jsx
<DatePicker
  label="Travel Start Date (Optional)"
  value={travelStartDate}
  onChange={setTravelStartDate}
  format="YYYY-MM-DD"
/>

<DatePicker
  label="Travel End Date (Optional)"
  value={travelEndDate}
  onChange={setTravelEndDate}
  format="YYYY-MM-DD"
/>
```

---

### 2. **Lead Display** (`POST /lead/get/` and `POST /lead/get_all/`)

**The API now returns travel dates** - display them in your UI:

```javascript
// Get single lead
const lead = await fetchLead(leadId);

// ✅ NEW - These fields are now in the response
console.log(lead.travel_start_date);  // "2024-03-01" or null
console.log(lead.travel_end_date);    // "2024-03-05" or null
```

**Display Example:**
```jsx
{lead.travel_start_date && lead.travel_end_date && (
  <div className="travel-dates">
    <span>Travel Dates: </span>
    <span>{formatDate(lead.travel_start_date)} - {formatDate(lead.travel_end_date)}</span>
  </div>
)}
```

**For Lead Cards (get_all_leads):**
```jsx
{leads.map(lead => (
  <LeadCard key={lead.lead_id}>
    <h3>{lead.customer.name}</h3>
    <p>{lead.package.name}</p>
    
    {/* ✅ NEW - Show travel dates if available */}
    {lead.travel_start_date && (
      <p className="travel-dates">
        📅 {formatDate(lead.travel_start_date)} - {formatDate(lead.travel_end_date)}
      </p>
    )}
  </LeadCard>
))}
```

---

### 3. **Lead Update Form** (`POST /lead/update/`)

**Allow users to update travel dates**:

```javascript
const updateLead = async (leadId, updates) => {
  const payload = {
    lead_id: leadId,
    created_by: userId,
    
    // ✅ NEW - You can now update these fields
    travel_start_date: "2024-03-10",  // Optional
    travel_end_date: "2024-03-15",    // Optional
    
    package_snapshot: {
      // ... existing package data
    }
  };

  const response = await fetch('/lead/update/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  return await response.json();
};
```

---

## 🎫 Booking APIs - What You Need to Do

### 1. **Booking Creation** (`POST /booking/add/`)

**Two options for handling travel dates:**

#### Option A: Use Lead's Travel Dates (Recommended)
```javascript
// ✅ EASIEST - Just don't send travel dates, they'll be copied from the lead
const createBooking = async (leadId) => {
  const payload = {
    lead_id: leadId,
    created_by: userId,
    // travel_start_date: NOT NEEDED - will use lead's date
    // travel_end_date: NOT NEEDED - will use lead's date
    itinerary_selections: [...],
    final_amount: 45000
  };

  const response = await fetch('/booking/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  return await response.json();
};
```

#### Option B: Override with Different Dates
```javascript
// ✅ If customer wants different dates than the lead
const createBooking = async (leadId, customDates) => {
  const payload = {
    lead_id: leadId,
    created_by: userId,
    
    // These will override the lead's dates
    travel_start_date: customDates.startDate,  // "2024-04-01"
    travel_end_date: customDates.endDate,      // "2024-04-05"
    
    itinerary_selections: [...],
    final_amount: 45000
  };

  const response = await fetch('/booking/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  return await response.json();
};
```

**UI Example:**
```jsx
// Show lead's dates with option to override
<div className="booking-dates">
  <p>Lead Travel Dates: {lead.travel_start_date} - {lead.travel_end_date}</p>
  
  <Checkbox
    label="Use different dates for booking"
    checked={useDifferentDates}
    onChange={setUseDifferentDates}
  />
  
  {useDifferentDates && (
    <>
      <DatePicker
        label="Booking Start Date"
        value={bookingStartDate}
        onChange={setBookingStartDate}
      />
      <DatePicker
        label="Booking End Date"
        value={bookingEndDate}
        onChange={setBookingEndDate}
      />
    </>
  )}
</div>
```

---

### 2. **Booking Update** (`POST /booking/update/`)

**No changes needed** - this already supported travel dates:

```javascript
// This already worked before
const updateBooking = async (transactionId, updates) => {
  const payload = {
    transaction_id: transactionId,
    travel_start_date: "2024-03-15",  // Already supported
    travel_end_date: "2024-03-20"     // Already supported
  };

  const response = await fetch('/booking/update/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  return await response.json();
};
```

---

## 📋 Summary Checklist

### Lead Forms
- [ ] Add optional date pickers for `travel_start_date` and `travel_end_date` to lead creation form
- [ ] Add optional date pickers to lead update form
- [ ] Display travel dates in lead detail view
- [ ] Display travel dates in lead cards/list view (if available)

### Booking Forms
- [ ] **Option 1 (Recommended)**: Don't send travel dates - they'll auto-copy from lead
- [ ] **Option 2**: Add UI to allow overriding lead's dates during booking creation
- [ ] Display travel dates in booking detail view (already working)

---

## 🎨 Date Format

**Always use ISO 8601 format**: `YYYY-MM-DD`

Examples:
- ✅ `"2024-03-01"`
- ✅ `"2024-12-25"`
- ❌ `"03/01/2024"`
- ❌ `"01-Mar-2024"`

---

## ❓ FAQs

**Q: Are travel dates required?**  
A: No, they're optional for both leads and bookings.

**Q: What happens if I don't send travel dates when creating a booking?**  
A: The booking will automatically copy the dates from the lead (if the lead has them).

**Q: Can I update travel dates after creating a lead/booking?**  
A: Yes, both lead and booking update APIs support updating travel dates.

**Q: What if the lead doesn't have travel dates?**  
A: The fields will be `null` in the API response. Handle this in your UI by checking if the values exist before displaying.

---

**Migration**: `0017_auto_20251127_1413.py`  
**Last Updated**: 2024-11-27

