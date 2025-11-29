# Quick Hotel Feature - Frontend Integration Guide

## 📋 Overview

The **Quick Hotel** feature allows users to add hotel data directly from the package page without selecting from the existing hotel database. This is useful when users find hotels on-the-fly for specific packages.

### Key Concept
- **Regular Hotel**: Selected from existing hotel database (has `hotel_id`)
- **Quick Hotel**: Added inline with minimal fields (no `hotel_id`, stored as data object)

---

## 🎯 Use Cases

### When to Use Quick Hotel?
- User finds a hotel quickly and wants to add it without going through the full hotel creation process
- Temporary/one-time hotel that doesn't need to be in the main hotel database
- Quick package creation workflow

### When to Use Regular Hotel?
- Hotel already exists in the database
- Hotel will be reused across multiple packages
- Full hotel details with amenities, policies, etc. are needed

---

## 🔧 API Changes

### 1. Package Creation/Update

#### Request Format

**Endpoint**: `POST /package/add/` or `POST /package/update/`

```json
{
  "tour_operator_id": 1,
  "created_by": 1,
  "name": "Kerala Delight",
  "destination_id": 5,
  "package_options": [
    {
      "name": "Standard",
      "amount": 50000,
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [10, 15],           // Regular hotels (existing)
          "quick_hotels": [                 // Quick hotels (new inline data)
            {
              "hotel_name": "Beach Resort",      // Required
              "room_type": "delux",              // Required: "standard", "delux", "premium", "suite"
              "price_per_night": 5000,           // Required
              "total_rooms": 2,                  // Required
              "address": "123 Beach Road",       // Optional
              "phone": "+91-9876543210"          // Optional
            }
          ]
        },
        {
          "day": 2,
          "hotel_ids": [20],
          "quick_hotels": []
        }
      ]
    }
  ]
}
```

#### Response Format

**Endpoint**: `POST /package/get/`

```json
{
  "id": 42,
  "name": "Kerala Delight",
  "package_options": [
    {
      "id": 100,
      "name": "Standard",
      "amount": 50000,
      "hotel_mappings": [
        {
          "day": 1,
          "hotel_ids": [10, 15],
          "quick_hotels": [
            {
              "id": 5,                           // QuickHotel ID (for reference)
              "hotel_name": "Beach Resort",
              "room_type": "delux",
              "price_per_night": 5000.00,
              "total_rooms": 2,
              "address": "123 Beach Road",
              "phone": "+91-9876543210"
            }
          ]
        }
      ]
    }
  ]
}
```

---

### 2. Lead Creation

#### Request Format

**Endpoint**: `POST /lead/add/`

When creating a lead from a package, the quick hotel data is automatically snapshotted. No special handling needed - just pass the package data as before.

```json
{
  "tour_operator_id": 1,
  "customer_id": 25,
  "created_by": 1,
  "package_snapshot": {
    // ... package data including quick_hotels in hotel_mappings
  }
}
```

#### Response Format

**Endpoint**: `POST /lead/get/`

```json
{
  "lead_id": 15,
  "package": {
    "package_options": [
      {
        "name": "Standard",
        "hotel_mappings": [
          {
            "day": 1,
            "hotel_ids": [10, 15],
            "quick_hotels": [              // Quick hotel data preserved as snapshot
              {
                "hotel_name": "Beach Resort",
                "room_type": "delux",
                "price_per_night": 5000.00,
                "total_rooms": 2,
                "address": "123 Beach Road",
                "phone": "+91-9876543210"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

### 3. Booking Creation

#### Request Format

**Endpoint**: `POST /booking/add/`

When customer selects a quick hotel for booking:

```json
{
  "lead_id": 15,
  "created_by": 1,
  "itinerary_selections": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "selected_hotel_id": 10,           // Option 1: Regular hotel
      "activities": [...]
    },
    {
      "day": 2,
      "title": "Beach Day",
      "quick_hotel_data": {              // Option 2: Quick hotel
        "hotel_name": "Beach Resort",
        "room_type": "delux",
        "price_per_night": 5000.00,
        "total_rooms": 2,
        "address": "123 Beach Road",
        "phone": "+91-9876543210"
      },
      "activities": [...]
    }
  ],
  "final_amount": 68500.00
}
```

**Important**: For each day, use **either** `selected_hotel_id` (regular hotel) **OR** `quick_hotel_data` (quick hotel), not both.

#### Response Format

**Endpoint**: `POST /booking/get/`

```json
{
  "transaction_id": 50,
  "booking_id": 50,
  "itinerary": [
    {
      "day": 1,
      "title": "Arrival in Kochi",
      "hotel": {
        "id": 10,                        // Regular hotel
        "name": "Grand Hotel",
        "description": "Luxury hotel",
        "images": [...],
        "quick_hotel_data": null
      }
    },
    {
      "day": 2,
      "title": "Beach Day",
      "hotel": {
        "id": null,                      // Quick hotel (no ID)
        "name": "Beach Resort",
        "description": "",
        "images": [],
        "quick_hotel_data": {            // Quick hotel details
          "hotel_name": "Beach Resort",
          "room_type": "delux",
          "price_per_night": 5000.00,
          "total_rooms": 2,
          "address": "123 Beach Road",
          "phone": "+91-9876543210"
        }
      }
    }
  ]
}
```

---

## 💻 Frontend Implementation

### 1. Package Creation/Edit Page

#### UI Components Needed

**Hotel Selection for Each Day:**

```jsx
// For each day in the package
<DayHotelSelector day={1}>
  {/* Existing Hotels Section */}
  <ExistingHotelsSection>
    <MultiSelect
      options={availableHotels}
      selected={selectedHotelIds}
      onChange={handleHotelSelection}
    />
  </ExistingHotelsSection>

  {/* Quick Hotel Section (NEW) */}
  <QuickHotelSection>
    <Button onClick={() => setShowQuickHotelForm(true)}>
      + Add Quick Hotel
    </Button>

    {quickHotels.map((qh, index) => (
      <QuickHotelCard key={index}>
        <div>{qh.hotel_name} - {qh.room_type}</div>
        <div>₹{qh.price_per_night}/night × {qh.total_rooms} rooms</div>
        <Button onClick={() => removeQuickHotel(index)}>Remove</Button>
      </QuickHotelCard>
    ))}
  </QuickHotelSection>
</DayHotelSelector>
```

#### Quick Hotel Form

```jsx
<QuickHotelForm>
  <Input
    label="Hotel Name *"
    value={hotelName}
    onChange={setHotelName}
    required
  />

  <Select
    label="Room Type *"
    value={roomType}
    onChange={setRoomType}
    options={[
      { value: "standard", label: "Standard" },
      { value: "delux", label: "Deluxe" },
      { value: "premium", label: "Premium" },
      { value: "suite", label: "Suite" }
    ]}
    required
  />

  <Input
    label="Price per Night *"
    type="number"
    value={pricePerNight}
    onChange={setPricePerNight}
    required
  />

  <Input
    label="Total Rooms *"
    type="number"
    value={totalRooms}
    onChange={setTotalRooms}
    required
  />

  <Input
    label="Address (Optional)"
    value={address}
    onChange={setAddress}
  />

  <Input
    label="Phone (Optional)"
    value={phone}
    onChange={setPhone}
  />

  <Button onClick={handleAddQuickHotel}>Add Hotel</Button>
</QuickHotelForm>
```

#### State Management

```javascript
// Package state structure
const [packageData, setPackageData] = useState({
  name: "",
  destination_id: null,
  package_options: [
    {
      name: "Standard",
      amount: 0,
      hotel_mappings: [
        {
          day: 1,
          hotel_ids: [10, 15],        // Regular hotels
          quick_hotels: [             // Quick hotels
            {
              hotel_name: "Beach Resort",
              room_type: "delux",
              price_per_night: 5000,
              total_rooms: 2,
              address: "123 Beach Road",
              phone: "+91-9876543210"
            }
          ]
        }
      ]
    }
  ]
});

// Add quick hotel to a specific day
const addQuickHotel = (optionIndex, day, quickHotelData) => {
  setPackageData(prev => {
    const updated = { ...prev };
    const mapping = updated.package_options[optionIndex]
      .hotel_mappings.find(m => m.day === day);

    if (!mapping.quick_hotels) {
      mapping.quick_hotels = [];
    }

    mapping.quick_hotels.push(quickHotelData);
    return updated;
  });
};

// Remove quick hotel
const removeQuickHotel = (optionIndex, day, quickHotelIndex) => {
  setPackageData(prev => {
    const updated = { ...prev };
    const mapping = updated.package_options[optionIndex]
      .hotel_mappings.find(m => m.day === day);

    mapping.quick_hotels.splice(quickHotelIndex, 1);
    return updated;
  });
};
```

---

### 2. Lead Display Page

When displaying a lead to the customer, show both regular and quick hotels as options:

```javascript
// Render hotel options for a day
const renderHotelOptions = (day, hotelMapping) => {
  return (
    <div>
      <h4>Hotel Options for Day {day}</h4>

      {/* Regular Hotels */}
      {hotelMapping.hotel_ids.map(hotelId => {
        const hotel = getHotelById(hotelId);
        return (
          <HotelCard key={hotelId} type="regular">
            <h5>{hotel.name}</h5>
            <p>{hotel.description}</p>
            <Images images={hotel.images} />
            <Radio
              name={`day-${day}-hotel`}
              value={hotelId}
              onChange={() => selectHotel(day, hotelId)}
            />
          </HotelCard>
        );
      })}

      {/* Quick Hotels */}
      {hotelMapping.quick_hotels.map((qh, index) => (
        <HotelCard key={`quick-${index}`} type="quick">
          <h5>{qh.hotel_name}</h5>
          <Badge>Quick Hotel</Badge>
          <p>Room Type: {qh.room_type}</p>
          <p>₹{qh.price_per_night}/night</p>
          <p>Rooms: {qh.total_rooms}</p>
          {qh.address && <p>Address: {qh.address}</p>}
          {qh.phone && <p>Phone: {qh.phone}</p>}
          <Radio
            name={`day-${day}-hotel`}
            value={`quick-${index}`}
            onChange={() => selectQuickHotel(day, qh)}
          />
        </HotelCard>
      ))}
    </div>
  );
};
```

---

### 3. Booking Creation Page

When customer clicks "Book Now", collect their selections:

```javascript
const handleBookNow = async () => {
  const itinerarySelections = [];

  for (const day of lead.itinerary_details) {
    const selection = customerSelections[day.day];

    const dayData = {
      day: day.day,
      title: day.title,
      description: day.description,
      activities: day.activities
    };

    // Check if customer selected a regular hotel or quick hotel
    if (selection.hotelType === 'regular') {
      dayData.selected_hotel_id = selection.hotelId;
    } else if (selection.hotelType === 'quick') {
      dayData.quick_hotel_data = selection.quickHotelData;
    }

    // Add transport selection
    if (selection.transportId) {
      dayData.selected_car_dealer_id = selection.transportId;
    }

    itinerarySelections.push(dayData);
  }

  const bookingData = {
    lead_id: lead.id,
    created_by: currentUser.id,
    package_snapshot: lead.package,
    itinerary_selections: itinerarySelections,
    base_amount: calculateBaseAmount(),
    final_amount: calculateFinalAmount(),
    // ... other booking fields
  };

  const response = await fetch('/booking/add/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookingData)
  });

  const result = await response.json();
  console.log('Booking created:', result.booking_id);
};
```

---

### 4. Booking Display Page

When displaying a booking, check if hotel is regular or quick:

```javascript
const renderBookingItinerary = (itinerary) => {
  return itinerary.map(day => {
    const isQuickHotel = day.hotel.quick_hotel_data !== null;

    return (
      <DayCard key={day.day}>
        <h4>Day {day.day}: {day.title}</h4>
        <p>{day.description}</p>

        <HotelSection>
          <h5>Hotel</h5>
          {isQuickHotel ? (
            // Quick Hotel Display
            <QuickHotelDisplay>
              <Badge>Quick Hotel</Badge>
              <h6>{day.hotel.quick_hotel_data.hotel_name}</h6>
              <p>Room Type: {day.hotel.quick_hotel_data.room_type}</p>
              <p>₹{day.hotel.quick_hotel_data.price_per_night}/night</p>
              <p>Rooms: {day.hotel.quick_hotel_data.total_rooms}</p>
              {day.hotel.quick_hotel_data.address && (
                <p>Address: {day.hotel.quick_hotel_data.address}</p>
              )}
              {day.hotel.quick_hotel_data.phone && (
                <p>Phone: {day.hotel.quick_hotel_data.phone}</p>
              )}
            </QuickHotelDisplay>
          ) : (
            // Regular Hotel Display
            <RegularHotelDisplay>
              <h6>{day.hotel.name}</h6>
              <p>{day.hotel.description}</p>
              <Images images={day.hotel.images} />
            </RegularHotelDisplay>
          )}
        </HotelSection>

        <TransportSection>
          <h5>Transport</h5>
          <p>{day.transport.name}</p>
          <p>{day.transport.car_type}</p>
        </TransportSection>

        <ActivitiesSection>
          <h5>Activities</h5>
          {day.activities.map(activity => (
            <ActivityCard key={activity.id}>
              <p>{activity.name}</p>
            </ActivityCard>
          ))}
        </ActivitiesSection>
      </DayCard>
    );
  });
};
```

---

## 🎨 UI/UX Recommendations

### Visual Distinction

Make it clear to users which hotels are "quick hotels" vs regular hotels:

1. **Badge/Label**: Add a "Quick Hotel" badge to quick hotel cards
2. **Icon**: Use a different icon (e.g., ⚡ lightning bolt) for quick hotels
3. **Color**: Use a subtle background color difference
4. **Information**: Show a tooltip explaining what a quick hotel is

### User Flow

**Package Creation:**
```
1. User selects day
2. User sees two options:
   - "Select from existing hotels" (shows hotel dropdown/list)
   - "Add quick hotel" (shows quick hotel form)
3. User can add multiple of each type per day
4. Both types are displayed in the same list with visual distinction
```

**Lead/Booking:**
```
1. Customer sees all hotel options (regular + quick) for each day
2. Visual distinction helps them understand the difference
3. Customer selects one hotel per day (can be either type)
4. Selection is passed to booking API appropriately
```

---

## ✅ Validation Rules

### Package Creation

```javascript
const validateQuickHotel = (quickHotel) => {
  const errors = {};

  // Required fields
  if (!quickHotel.hotel_name || quickHotel.hotel_name.trim() === '') {
    errors.hotel_name = 'Hotel name is required';
  }

  if (!quickHotel.room_type) {
    errors.room_type = 'Room type is required';
  }

  if (!quickHotel.price_per_night || quickHotel.price_per_night <= 0) {
    errors.price_per_night = 'Price per night must be greater than 0';
  }

  if (!quickHotel.total_rooms || quickHotel.total_rooms <= 0) {
    errors.total_rooms = 'Total rooms must be greater than 0';
  }

  // Optional fields validation
  if (quickHotel.phone && !/^[+]?[\d\s-()]+$/.test(quickHotel.phone)) {
    errors.phone = 'Invalid phone number format';
  }

  return Object.keys(errors).length > 0 ? errors : null;
};
```

### Booking Creation

```javascript
const validateItinerarySelection = (selection) => {
  // Each day must have either selected_hotel_id OR quick_hotel_data, not both
  const hasRegularHotel = !!selection.selected_hotel_id;
  const hasQuickHotel = !!selection.quick_hotel_data;

  if (hasRegularHotel && hasQuickHotel) {
    return 'Cannot select both regular hotel and quick hotel for the same day';
  }

  if (!hasRegularHotel && !hasQuickHotel) {
    return 'Must select a hotel (regular or quick) for each day';
  }

  return null;
};
```

---

## 🔍 Testing Checklist

### Package Module
- [ ] Create package with only regular hotels
- [ ] Create package with only quick hotels
- [ ] Create package with mix of regular and quick hotels
- [ ] Edit package - add quick hotel to existing day
- [ ] Edit package - remove quick hotel from day
- [ ] Edit package - update quick hotel details
- [ ] View package - verify quick hotels display correctly

### Lead Module
- [ ] Create lead from package with quick hotels
- [ ] View lead - verify quick hotels are preserved
- [ ] Verify quick hotel data is snapshotted (not referenced)

### Booking Module
- [ ] Create booking selecting regular hotel
- [ ] Create booking selecting quick hotel
- [ ] Create booking with mix of regular and quick hotels
- [ ] View booking - verify quick hotel details display correctly
- [ ] Verify quick hotel data is preserved in booking

### Edge Cases
- [ ] Package with 0 hotels (neither regular nor quick)
- [ ] Package with multiple quick hotels on same day
- [ ] Quick hotel with only required fields (no address/phone)
- [ ] Quick hotel with all fields filled
- [ ] Update package - change quick hotel to regular hotel
- [ ] Update package - change regular hotel to quick hotel

---

## 📞 Support

### Room Type Options

The `room_type` field accepts these values:
- `"standard"` - Standard Room
- `"delux"` - Deluxe Room
- `"premium"` - Premium Room
- `"suite"` - Suite

### Common Issues

**Q: Can I edit a quick hotel after creating it?**
A: Yes, when editing a package, you can modify or remove quick hotels. However, once a lead or booking is created, the quick hotel data is snapshotted and cannot be edited (this preserves the booking history).

**Q: Can I convert a quick hotel to a regular hotel?**
A: No direct conversion. You need to remove the quick hotel and add a regular hotel from the database.

**Q: What happens to quick hotels when a package is deleted?**
A: Quick hotels are deleted along with the package (CASCADE delete). However, leads and bookings preserve the quick hotel data as snapshots.

**Q: Can I search/filter by quick hotels?**
A: Quick hotels are package-specific and not stored in the main hotel database, so they won't appear in hotel search/filter results.

---

## 🚀 Migration Guide

If you have existing code that handles hotel selections, here's what needs to change:

### Before (Old Code)
```javascript
// Only handled regular hotels
const hotelMapping = {
  day: 1,
  hotel_ids: [10, 15]
};
```

### After (New Code)
```javascript
// Handle both regular and quick hotels
const hotelMapping = {
  day: 1,
  hotel_ids: [10, 15],        // Regular hotels
  quick_hotels: [             // Quick hotels (NEW)
    {
      hotel_name: "Beach Resort",
      room_type: "delux",
      price_per_night: 5000,
      total_rooms: 2
    }
  ]
};
```

### Backward Compatibility

The API is **fully backward compatible**:
- If you don't send `quick_hotels`, it defaults to an empty array
- Existing packages without quick hotels continue to work as before
- You can gradually adopt the quick hotel feature

---

## 📝 Summary

### Key Points
1. **Two types of hotels**: Regular (from database) and Quick (inline data)
2. **Mutually exclusive per selection**: Customer picks either regular OR quick hotel per day
3. **Snapshot pattern**: Quick hotel data is preserved in leads and bookings
4. **Optional fields**: Only hotel_name, room_type, price_per_night, and total_rooms are required
5. **Backward compatible**: Existing code continues to work without changes

### Next Steps
1. Update package creation UI to support quick hotel form
2. Update lead display to show quick hotels alongside regular hotels
3. Update booking creation to handle quick hotel selections
4. Update booking display to show quick hotel details
5. Test thoroughly with the checklist above

For questions or issues, please contact the backend team.


