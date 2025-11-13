# Booking (Transaction) API - Quick Reference

## 📋 TL;DR

You already have a **Lead** displayed in the UI. When customer clicks **"Book Now"**, you need to:
1. Show selection UI (customer picks 1 hotel + 1 transport per day)
2. Call `POST /transaction/add/` with `lead_id` + customer's selections
3. Show booking confirmation

---

## 🎯 The "Book Now" Button

### What You Have
- A Lead with multiple hotel/transport options per day
- Customer has reviewed the options

### What You Need to Do

**Step 1: Customer Selection UI**
```javascript
// For each day, show hotel options and let customer pick ONE
Day 1: Arrival in Kochi
  Hotels:
    ○ Hotel A - $100/night
    ● Hotel B - $150/night (Selected)
    ○ Hotel C - $200/night

  Transport:
    ● Sedan - $50/day (Selected)
    ○ SUV - $80/day
```

**Step 2: Call Booking API**

```javascript
POST /transaction/add/
{
  "lead_id": 3,  // The lead being booked
  "created_by": 1,

  // Copy from lead.package
  "package_snapshot": {
    "name": "Kerala Delight",
    "description": "...",
    "inclusions": [...],
    "exclusions": [...],
    "amenities": [...],
    "policies": [...],
    "images": [...]
  },

  // Customer's selections (IDs only)
  "itinerary_selections": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "selected_hotel_id": 4,  // Customer picked this
      "selected_car_dealer_id": 2,  // Customer picked this
      "activities": [...]
    },
    {
      "day": 2,
      "selected_hotel_id": 7,
      "selected_car_dealer_id": 3,
      "activities": [...]
    }
  ],

  // Financial details
  "base_amount": 70000.00,
  "discount_amount": 5000.00,
  "taxes": 3500.00,
  "final_amount": 68500.00,
  "amount_paid": 20000.00,  // Initial payment
  "amount_due": 48500.00,

  // Booking details
  "travel_start_date": "2025-12-01",
  "travel_end_date": "2025-12-05",
  "booking_status": "confirmed",
  "payment_status": "partial",
  "booking_notes": "Customer requested early check-in"
}
```

**Step 3: Show Confirmation**
```javascript
// API returns
{
  "message": "Transaction created successfully",
  "transaction_id": 15
}

// Navigate to booking confirmation page
```

---

## 🔑 Key Fields Explained

### Status Fields (Two separate fields now)

**booking_status:**
- `"pending"` - Booking not yet confirmed
- `"confirmed"` - Booking confirmed
- `"cancelled"` - Booking cancelled
- `"completed"` - Trip completed

**payment_status:**
- `"unpaid"` - No payment received
- `"partial"` - Partial payment received
- `"paid"` - Fully paid
- `"refunded"` - Payment refunded

### Payment Fields (Better tracking)

| Field | Description | Example |
|-------|-------------|---------|
| `base_amount` | Original package price | 70000.00 |
| `discount_amount` | Discount applied | 5000.00 |
| `taxes` | Tax amount | 3500.00 |
| `final_amount` | Total to pay | 68500.00 |
| `amount_paid` | Amount already paid | 20000.00 |
| `amount_due` | Remaining amount | 48500.00 |

---

## 🎨 UI Components Needed

### 1. Hotel Selection Component (Per Day)

```javascript
// For each day in lead.itinerary_details
<HotelSelector day={day}>
  {day.hotel_details.map(hotel => (
    <HotelOption
      key={hotel.id}
      hotel={hotel}
      selected={selectedHotelId === hotel.id}
      onSelect={() => setSelectedHotelId(hotel.id)}
    >
      <h4>{hotel.name}</h4>
      <p>{hotel.description}</p>
      <span>₹{hotel.price_per_night}/night</span>
      <img src={hotel.images[0]?.image_url} />
    </HotelOption>
  ))}
</HotelSelector>
```

### 2. Transport Selection Component (Per Day)

```javascript
<TransportSelector day={day}>
  {day.car_dealer_details.map(transport => (
    <TransportOption
      key={transport.id}
      transport={transport}
      selected={selectedTransportId === transport.id}
      onSelect={() => setSelectedTransportId(transport.id)}
    >
      <h4>{transport.car_type_name}</h4>
      <p>{transport.car_dealer_name}</p>
      <span>₹{transport.price}/day</span>
    </TransportOption>
  ))}
</TransportSelector>
```

### 3. "Book Now" Button Handler

```javascript
const handleBookNow = async () => {
  // Collect customer selections
  const selections = lead.itinerary_details.map(day => ({
    day: day.day,
    title: day.title,
    description: day.description,
    selected_hotel_id: customerSelections[day.day].hotelId,
    selected_car_dealer_id: customerSelections[day.day].transportId,
    activities: day.activities
  }));

  // Build booking request
  const bookingData = {
    lead_id: lead.id,
    created_by: currentUser.id,
    package_snapshot: {
      name: lead.package.name,
      description: lead.package.description,
      inclusions: lead.package.inclusions,
      exclusions: lead.package.exclusions,
      amenities: lead.package.amenities,
      policies: lead.package.policies,
      images: lead.package.images
    },
    itinerary_selections: selections,
    base_amount: calculateBaseAmount(),
    discount_amount: discount,
    taxes: calculateTaxes(),
    final_amount: calculateTotal(),
    amount_paid: initialPayment,
    amount_due: calculateTotal() - initialPayment,
    travel_start_date: travelDates.start,
    travel_end_date: travelDates.end,
    booking_status: "confirmed",
    payment_status: initialPayment > 0 ? "partial" : "unpaid",
    booking_notes: notes
  };

  // Call API
  const response = await fetch('/transaction/add/', {
    method: 'POST',
    body: JSON.stringify(bookingData)
  });

  const result = await response.json();

  // Navigate to confirmation
  navigate(`/bookings/${result.transaction_id}`);
};
```

---

## 📊 What Changed from Old System

| What | OLD | NEW |
|------|-----|-----|
| **Entry Point** | Direct from package | From Lead (required) |
| **Hotel/Transport** | Full object embedded | Just IDs (`selected_hotel_id`) |
| **Field Name** | `itinerary_details` | `itinerary_selections` |
| **Status** | Single `status` | `booking_status` + `payment_status` |
| **Payment** | Only `final_amount` | `base_amount`, `discount`, `taxes`, `paid`, `due` |
| **Required Field** | `customer_id` | `lead_id` (customer comes from lead) |

---

## ✅ Checklist for UI Team

- [ ] Add "Book Now" button on Lead detail page
- [ ] Create hotel selection UI (show all options, select one per day)
- [ ] Create transport selection UI (show all options, select one per day)
- [ ] Update booking creation to use `lead_id` + `itinerary_selections`
- [ ] Update status displays to show both `booking_status` and `payment_status`
- [ ] Update payment tracking to show `amount_paid` and `amount_due`
- [ ] Test complete flow: Lead → Select Options → Book → Confirmation

---

## 🆘 Need Help?

**Full Documentation:** `docs/transaction_api_update_for_ui.md`

**Common Questions:**

**Q: Where do I get the lead data?**
A: You already have it displayed in the UI. Use the same lead object.

**Q: What if customer doesn't select a hotel/transport for a day?**
A: Make selection mandatory in UI, or pass `null` for optional days.

**Q: Can I update the booking later?**
A: Yes, use `POST /transaction/update/` to update booking/payment status.

**Q: What about the old transaction APIs?**
A: They're deprecated and return HTTP 410 error. Use the new Lead-based flow.

