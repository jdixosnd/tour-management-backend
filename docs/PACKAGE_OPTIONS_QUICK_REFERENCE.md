# Package Options - Quick Reference Guide

## 🚀 TL;DR

Package Options feature is **COMPLETE** and integrated across:
- ✅ Packages
- ✅ Leads  
- ✅ Bookings

**Migration:** `0013_auto_20251125_0620.py` - ✅ Applied

---

## 📦 API Quick Reference

### 1. Package APIs

**Get Package** - Returns package with options
```json
GET /package/get/
Response includes:
{
  "package_options": [
    {
      "id": 1,
      "name": "Standard",
      "amount": 20000,
      "hotel_mappings": [{"day": 1, "hotel_ids": [101, 102]}]
    }
  ]
}
```

### 2. Lead APIs

**Add Lead** - Include package_options in snapshot
```json
POST /lead/add/
{
  "package_snapshot": {
    "package_options": [...]  // Copy from package response
  }
}
```

**Get Lead** - Returns lead with options
```json
POST /lead/get/
Response includes:
{
  "package": {
    "package_options": [...]  // All options offered to customer
  }
}
```

### 3. Booking APIs

**Add Booking** - Include selected option
```json
POST /booking/add/
{
  "selected_package_option_name": "Deluxe",
  "selected_package_option_amount": 30000
}
```

**Get Booking** - Returns selected option
```json
POST /booking/get/
Response includes:
{
  "package": {
    "selected_option": {
      "name": "Deluxe",
      "amount": 30000
    }
  }
}
```

---

## 🗄️ Database Tables

### New Tables:
1. `LeadPackageOption` - Package options snapshot in leads
2. `LeadPackageOptionHotelMapping` - Hotel mappings for lead options

### Modified Tables:
- `Transaction` - Added `selected_package_option_name` and `selected_package_option_amount`

---

## 💻 Frontend Integration

### Step 1: Create Lead from Package
```javascript
const packageData = await fetchPackage(packageId);
const leadData = {
  package_snapshot: packageData  // Includes package_options
};
await createLead(leadData);
```

### Step 2: Display Options to Customer
```javascript
const leadData = await fetchLead(leadId);
leadData.package.package_options.forEach(option => {
  // Show option name, price, and hotels
});
```

### Step 3: Create Booking with Selected Option
```javascript
const selectedOption = leadData.package.package_options[1]; // Customer chose Deluxe
const bookingData = {
  selected_package_option_name: selectedOption.name,
  selected_package_option_amount: selectedOption.amount,
  base_amount: selectedOption.amount,
  // ... rest of booking data
};
await createBooking(bookingData);
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `PACKAGE_OPTIONS_IMPLEMENTATION_SUMMARY.md` | Complete technical summary |
| `PACKAGE_OPTIONS_LEAD_BOOKING_INTEGRATION.md` | Lead & Booking API changes |
| `package_options_api_documentation.md` | Package API documentation |
| `FRONTEND_PACKAGE_OPTIONS_GUIDE.md` | Detailed frontend guide |
| `PACKAGE_OPTIONS_QUICK_START.md` | Package options quick start |

---

## ✅ Backward Compatibility

- ✅ Packages without options work (empty array)
- ✅ Leads without options work
- ✅ Bookings without selected option work (null)
- ✅ Legacy `package_amount` field retained

---

## 🧪 Testing

**Run Model Tests:**
```bash
python test_package_options_integration.py
```

**Manual Testing:**
1. Create package with options
2. Create lead from package
3. Verify lead has options
4. Create booking with selected option
5. Verify booking shows selected option

---

## 🎯 Next Steps

**Backend:** ✅ Complete

**Frontend:**
1. Update lead creation UI
2. Display package options
3. Add option selection in booking flow
4. Test end-to-end

---

## 📞 Quick Help

**Issue:** Lead doesn't show package_options
- **Check:** Package has `package_options` array
- **Check:** Lead was created with `package_snapshot` including options

**Issue:** Booking doesn't show selected_option
- **Check:** Booking was created with `selected_package_option_name` and `selected_package_option_amount`

**Issue:** Old data not working
- **Solution:** Feature is backward compatible - old data will have empty arrays or null values

---

## 🔗 Related Files

**Models:** `tour_management/models.py` (lines 728-773, 817-819)
**Lead Controller:** `tour_management/controllers/lead.py`
**Booking Controller:** `tour_management/controllers/booking.py`
**Admin:** `tour_management/admin.py` (lines 212-233)
**Migration:** `tour_management/migrations/0013_auto_20251125_0620.py`
**Tests:** `test_package_options_integration.py`

