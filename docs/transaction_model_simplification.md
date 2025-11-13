# Transaction Model Simplification

## Overview

The Transaction model has been simplified to reference the Lead model instead of storing duplicate snapshot data. This change eliminates redundancy since all package snapshot data is already stored in the LeadPackage model.

---

## Model Changes

### Old Transaction Model (REMOVED)
- Stored complete package snapshot (name, description, type, etc.)
- Stored package-level amenities, inclusions, exclusions, policies, images
- Had separate `TransactionDayDetails` and `TransactionItineraryDetails` models
- Total: 3 models with ~100+ fields

### New Transaction Model (SIMPLIFIED)
- References Lead (which contains all package snapshot data via LeadPackage)
- Stores only booking-specific information:
  - Booking status (pending, confirmed, cancelled, completed)
  - Payment status (unpaid, partial, paid, refunded)
  - Travel dates (start and end)
  - Financial details (base amount, discount, taxes, final amount, paid, due)
  - Booking notes and cancellation reason
  - Timestamps (created, updated, confirmed, cancelled)
- Total: 1 model with ~20 fields

---

## Database Changes

### Removed Models
- `TransactionDayDetails` - Day-wise hotel, room, car dealer snapshots
- `TransactionItineraryDetails` - Activity snapshots per day

### Removed Fields from Transaction
- `package` (ForeignKey)
- `destination` (ForeignKey)
- `package_name`, `package_description`, `package_type`
- `pax_size`, `contains_travel_fare`, `transport_type`, `no_of_days`
- `package_amount`, `proposed_package_amount`, `original_package_amount`, `margin_of_profit`
- `package_amenities`, `package_inclusions`, `package_exclusions`, `package_policies`, `package_images`

### Added Fields to Transaction
- `lead` (ForeignKey to Lead) - References the lead containing package snapshot
- `booking_status` - Booking state (pending/confirmed/cancelled/completed)
- `payment_status` - Payment state (unpaid/partial/paid/refunded)
- `travel_start_date`, `travel_end_date` - Travel dates
- `base_amount` - Base package amount from lead
- `final_amount` - Final amount after discount and taxes
- `amount_paid`, `amount_due` - Payment tracking
- `booking_notes`, `cancellation_reason` - Additional notes
- `updated_at`, `confirmed_at`, `cancelled_at` - Timestamps

---

## API Changes

### New Transaction APIs

All new APIs are in `tour_management/controllers/transaction_new.py`

#### 1. Add Transaction
**Endpoint:** `POST /transaction/add/`

**Request:**
```json
{
  "lead_id": 3,
  "created_by": 1,
  "base_amount": 70000.00,
  "discount_amount": 5000.00,
  "taxes": 3500.00,
  "final_amount": 68500.00,
  "amount_paid": 20000.00,
  "amount_due": 48500.00,
  "booking_status": "confirmed",
  "payment_status": "partial",
  "travel_start_date": "2025-12-01",
  "travel_end_date": "2025-12-05",
  "booking_notes": "Customer requested early check-in"
}
```

**Response:**
```json
{
  "message": "Transaction created successfully",
  "transaction_id": 5
}
```

#### 2. Get Transaction
**Endpoint:** `POST /transaction/get/`

**Request:**
```json
{
  "transaction_id": 5
}
```

**Response:**
```json
{
  "transaction_id": 5,
  "lead_id": 3,
  "customer": {
    "id": 1,
    "name": "John Doe",
    "phone": "1234567890",
    "email": "john@example.com",
    "address": "123 Main St"
  },
  "booking_status": "confirmed",
  "payment_status": "partial",
  "travel_start_date": "2025-12-01",
  "travel_end_date": "2025-12-05",
  "financial_details": {
    "base_amount": 70000.00,
    "discount_amount": 5000.00,
    "taxes": 3500.00,
    "final_amount": 68500.00,
    "amount_paid": 20000.00,
    "amount_due": 48500.00
  },
  "booking_notes": "Customer requested early check-in",
  "cancellation_reason": null,
  "created_at": "2025-11-13T10:00:00",
  "updated_at": "2025-11-13T10:30:00",
  "confirmed_at": "2025-11-13T10:30:00",
  "cancelled_at": null
}
```

**Note:** To get the complete package snapshot, call `GET /lead/get/` with the `lead_id` from the transaction response.

#### 3. Update Transaction
**Endpoint:** `POST /transaction/update/`

**Request:**
```json
{
  "transaction_id": 5,
  "payment_status": "paid",
  "amount_paid": 68500.00,
  "amount_due": 0.00,
  "booking_notes": "Full payment received"
}
```

**Response:**
```json
{
  "message": "Transaction updated successfully",
  "transaction_id": 5
}
```

#### 4. Get All Transactions
**Endpoint:** `POST /transaction/get_all/`

**Request:**
```json
{
  "tour_operator_id": 1,
  "booking_status": "confirmed",
  "payment_status": "partial",
  "page": 1,
  "page_size": 12
}
```

---

## Migration

Run the migration to apply changes:

```bash
python manage.py migrate tour_management 0007_simplify_transaction_model
```

**Warning:** This migration will:
- Drop `TransactionDayDetails` and `TransactionItineraryDetails` tables
- Remove snapshot fields from `Transaction` table
- Add new booking-specific fields

Make sure to backup your database before running the migration!

---

## Benefits

1. **No Data Duplication** - Package snapshot stored once in LeadPackage, not duplicated in Transaction
2. **Simpler Model** - Transaction focuses only on booking/payment information
3. **Easier Maintenance** - Changes to package data only need to update Lead, not Transaction
4. **Better Separation** - Clear separation between package proposal (Lead) and booking (Transaction)
5. **Smaller Database** - Significantly reduced storage requirements

---

## Workflow

1. **Create Package** → Package API
2. **Create Lead from Package** → Lead API (stores complete package snapshot)
3. **Share Lead with Customer** → Lead contains all package details
4. **Customer Confirms** → Create Transaction from Lead
5. **Transaction References Lead** → All package data accessible via lead_id
6. **Update Booking/Payment** → Update Transaction (booking-specific fields only)


