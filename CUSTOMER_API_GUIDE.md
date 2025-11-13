# Customer API Guide for UI Team

## Base URL
All endpoints use `POST` method and return JSON responses.

---

## 1. Add Customer
**Endpoint:** `/customer/add/`

**Request:**
```json
{
  "tour_operator_id": 1,
  "name": "John Doe",
  "phone": "1234567890",
  "email": "john@example.com",    // optional
  "address": "123 Main St"         // optional
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Customer added successfully",
  "customer_id": 1
}
```

---

## 2. Get Customers
**Endpoint:** `/customer/get/`

**Request:**
```json
{
  "tour_operator_id": 1,      // REQUIRED - only returns customers for this operator
  "customer_id": 1,           // optional - get specific customer
  "phone": "1234",            // optional - search by phone
  "email": "john",            // optional - search by email
  "name": "John",             // optional - search by name
  "page": 1,                  // optional
  "page_size": 10             // optional
}
```

**Note:** Each tour operator can only see their own customers (data isolation).

**Response:**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "tour_operator_id": 1,
      "tour_operator_name": "ABC Tours",
      "name": "John Doe",
      "phone": "1234567890",
      "email": "john@example.com",
      "address": "123 Main St",
      "created_at": "2025-11-12 10:30:00"
    }
  ],
  "count": 1,
  "next": null,
  "previous": null
}
```

---

## 3. Update Customer
**Endpoint:** `/customer/update/`

**Request:**
```json
{
  "customer_id": 1,           // required
  "name": "John Smith",       // optional
  "phone": "9876543210",      // optional
  "email": "new@example.com", // optional
  "address": "456 Oak Ave"    // optional
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Customer updated successfully"
}
```

---

## 4. Delete Customer
**Endpoint:** `/customer/delete/`

**Request:**
```json
{
  "customer_id": 1
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Customer 'John Doe' deleted successfully"
}
```

**Note:** Delete will fail (code 409) if customer has associated leads or transactions.

---

## Error Codes
- `200` - Success
- `400` - Missing required fields or invalid data
- `404` - Customer/Tour operator not found
- `409` - Duplicate phone number or customer has dependencies
- `500` - Server error

