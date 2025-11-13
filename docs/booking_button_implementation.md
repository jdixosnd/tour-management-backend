# "Book Now" Button - Implementation Guide

## 🎯 Overview

This guide explains how to implement the "Book Now" button that converts a Lead into a Booking (Transaction).

---

## 📍 Where is the Button?

**Location:** Lead Detail Page

**When to show:**
- Lead status is "accepted" or "shared"
- Customer has reviewed the options
- Lead has at least one itinerary day with hotel/transport options

---

## 🔄 Complete Flow

### 1. Lead Detail Page (Before Booking)

```
┌─────────────────────────────────────────────┐
│ Lead #3 - Kerala Delight                   │
│ Customer: John Doe                          │
│ Status: Accepted                            │
├─────────────────────────────────────────────┤
│                                             │
│ Day 1: Arrival in Kochi                    │
│   Hotels: 3 options                         │
│   Transport: 2 options                      │
│   Activities: Sightseeing                   │
│                                             │
│ Day 2: Kochi Sightseeing                   │
│   Hotels: 3 options                         │
│   Transport: 2 options                      │
│   Activities: Beach visit                   │
│                                             │
│ [View Details] [Book Now] ← This button    │
└─────────────────────────────────────────────┘
```

### 2. Customer Selection Modal (After clicking "Book Now")

```
┌─────────────────────────────────────────────┐
│ Complete Your Booking                       │
├─────────────────────────────────────────────┤
│                                             │
│ Day 1: Arrival in Kochi                    │
│ ┌─────────────────────────────────────────┐ │
│ │ Select Hotel:                           │ │
│ │ ○ Hotel A - ₹5,000/night               │ │
│ │ ● Hotel B - ₹7,500/night (Selected)    │ │
│ │ ○ Hotel C - ₹10,000/night              │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ Select Transport:                       │ │
│ │ ● Sedan - ₹2,500/day (Selected)        │ │
│ │ ○ SUV - ₹4,000/day                     │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Day 2: Kochi Sightseeing                   │
│ [Similar selection UI]                     │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Payment Details                         │ │
│ │ Base Amount: ₹70,000                    │ │
│ │ Discount: -₹5,000                       │ │
│ │ Taxes: +₹3,500                          │ │
│ │ Total: ₹68,500                          │ │
│ │                                         │ │
│ │ Pay Now: [₹20,000]                      │ │
│ │ Pay Later: ₹48,500                      │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Travel Dates:                               │
│ Start: [2025-12-01] End: [2025-12-05]      │
│                                             │
│ Notes: [Optional booking notes]             │
│                                             │
│ [Cancel] [Confirm Booking]                  │
└─────────────────────────────────────────────┘
```

### 3. API Call (When clicking "Confirm Booking")

```javascript
const handleConfirmBooking = async () => {
  const response = await fetch('/transaction/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      lead_id: lead.id,
      created_by: currentUser.id,
      
      package_snapshot: {
        name: lead.package.name,
        description: lead.package.description,
        type: lead.package.type,
        pax_size: lead.package.pax_size,
        no_of_days: lead.package.no_of_days,
        inclusions: lead.package.inclusions,
        exclusions: lead.package.exclusions,
        amenities: lead.package.amenities,
        policies: lead.package.policies,
        images: lead.package.images
      },
      
      itinerary_selections: customerSelections,
      
      base_amount: 70000.00,
      discount_amount: 5000.00,
      taxes: 3500.00,
      final_amount: 68500.00,
      amount_paid: 20000.00,
      amount_due: 48500.00,
      
      travel_start_date: "2025-12-01",
      travel_end_date: "2025-12-05",
      
      booking_status: "confirmed",
      payment_status: "partial",
      
      booking_notes: notes
    })
  });
  
  const result = await response.json();
  
  if (result.transaction_id) {
    // Success - navigate to booking confirmation
    navigate(`/bookings/${result.transaction_id}`);
  }
};
```

### 4. Booking Confirmation Page

```
┌─────────────────────────────────────────────┐
│ ✓ Booking Confirmed!                        │
│ Booking ID: #15                             │
├─────────────────────────────────────────────┤
│                                             │
│ Customer: John Doe                          │
│ Package: Kerala Delight                     │
│ Travel Dates: Dec 1-5, 2025                │
│                                             │
│ Day 1: Arrival in Kochi                    │
│   Hotel: Hotel B                            │
│   Transport: Sedan                          │
│                                             │
│ Day 2: Kochi Sightseeing                   │
│   Hotel: Hotel D                            │
│   Transport: SUV                            │
│                                             │
│ Payment Summary:                            │
│   Total: ₹68,500                            │
│   Paid: ₹20,000                             │
│   Due: ₹48,500                              │
│                                             │
│ Status: Confirmed | Payment: Partial        │
│                                             │
│ [Download Invoice] [Send to Customer]       │
└─────────────────────────────────────────────┘
```

---

## 💡 Implementation Tips

1. **Validate selections** - Ensure customer has selected hotel/transport for all days before allowing booking
2. **Calculate totals** - Recalculate amounts based on selected hotels/transports
3. **Handle errors** - Show clear error messages if booking fails
4. **Update lead status** - Optionally update lead status to "converted" after successful booking
5. **Send confirmation** - Send booking confirmation email to customer

---

## 📚 Related Documentation

- Full API details: `docs/transaction_api_update_for_ui.md`
- Quick reference: `docs/transaction_api_quick_reference.md`

