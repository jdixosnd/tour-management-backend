# Dashboard API Documentation

This guide details the API endpoints for the Tour Operator Dashboard and provides recommendations on how to visualize the data.

## Base URL
Assuming the backend is running at `http://localhost:8000` (or your production domain).

## Authentication & Context
All dashboard endpoints require a `tour_operator_id` query parameter to filter data for the specific organization.
*   **Method:** GET
*   **Params:** `?tour_operator_id=<id>`

---

## 1. Sales & Revenue Analytics
**Endpoint:** `/dashboard/sales/`

Returns high-level financial metrics.

### Request
```http
GET /dashboard/sales/?tour_operator_id=1
```

### Response
```json
{
  "status": "success",
  "data": {
    "total_revenue": 150000.00,
    "outstanding_payments": {
      "paid": 100000.00,
      "due": 50000.00
    },
    "revenue_trend": [
      { "month": "2023-11", "revenue": 12000.00 },
      { "month": "2023-12", "revenue": 15000.00 }
    ],
    "revenue_by_package_type": [
      { "type": "HoneyMoon", "revenue": 80000.00 },
      { "type": "Family", "revenue": 70000.00 }
    ]
  }
}
```

### 📊 Recommended Visualizations
| Data Field | Chart Type | Description |
| :--- | :--- | :--- |
| `total_revenue` | **Big Number / KPI Card** | Display as a prominent currency figures (e.g., "$150k"). |
| `outstanding_payments` | **Stacked Bar Chart** | One bar showing split between "Paid" vs "Due". |
| `revenue_trend` | **Line / Area Chart** | X-Axis: `month`, Y-Axis: `revenue`. Shows growth over time. |
| `revenue_by_package_type` | **Donut Chart** | Segments for each package type showing their contribution to total revenue. |

---

## 2. Booking Analytics
**Endpoint:** `/dashboard/bookings/`

Returns operational booking data.

### Request
```http
GET /dashboard/bookings/?tour_operator_id=1
```

### Response
```json
{
  "status": "success",
  "data": {
    "booking_status_distribution": [
      { "status": "confirmed", "count": 15 },
      { "status": "pending", "count": 5 },
      { "status": "cancelled", "count": 2 }
    ],
    "monthly_booking_volume": [
      { "month": "2023-11", "count": 10 },
      { "month": "2023-12", "count": 12 }
    ],
    "upcoming_trips": [
      {
        "id": 101,
        "package_name": "Mystical Manali",
        "customer__name": "John Doe",
        "travel_start_date": "2024-01-10",
        "travel_end_date": "2024-01-15"
      }
    ],
    "total_cancellations": 2
  }
}
```

### 📊 Recommended Visualizations
| Data Field | Chart Type | Description |
| :--- | :--- | :--- |
| `booking_status_distribution` | **Pie / Donut Chart** | Shows percentage of bookings in each state (Confirmed, Pending, etc.). |
| `monthly_booking_volume` | **Vertical Bar Chart** | X-Axis: `month`, Y-Axis: `count`. Tracks demand seasonality. |
| `upcoming_trips` | **List / Calendar View** | Simple table or list ordered by date. Highlights immediate operations. |
| `total_cancellations` | **KPI Card (Red)** | Display as a simple number, potentially with a red warning color. |

---

## 3. Lead Analytics
**Endpoint:** `/dashboard/leads/`

Returns sales pipeline health.

### Request
```http
GET /dashboard/leads/?tour_operator_id=1
```

### Response
```json
{
  "status": "success",
  "data": {
    "lead_status_distribution": [
      { "status": "New", "count": 20 },
      { "status": "Follow Up", "count": 10 },
      { "status": "Closed", "count": 5 }
    ],
    "conversion_rate": 15.5,
    "leads_by_destination": [
      { "destination__name": "Kerala", "count": 12 },
      { "destination__name": "Goa", "count": 8 }
    ]
  }
}
```

### 📊 Recommended Visualizations
| Data Field | Chart Type | Description |
| :--- | :--- | :--- |
| `lead_status_distribution` | **Funnel Chart** | "New" -> "Follow Up" -> "Closed". Visualizes the drop-off in the pipeline. |
| `conversion_rate` | **Radial Gauge / % Card** | Shows efficiency. E.g., a gauge filled to 15.5%. |
| `leads_by_destination` | **Horizontal Bar Chart** | Bars for each destination, sorted by count. |

---

## 4. Product Analytics
**Endpoint:** `/dashboard/products/`

Returns performance of destinations and packages.

### Request
```http
GET /dashboard/products/?tour_operator_id=1
```

### Response
```json
{
  "status": "success",
  "data": {
    "top_destinations": [
      { "destination__name": "Manali", "bookings": 25 },
      { "destination__name": "Shimla", "bookings": 18 }
    ],
    "top_packages": [
      { "package_name": "Manali Special", "bookings": 15, "revenue": 50000.00 },
      { "package_name": "Goa Party", "bookings": 10, "revenue": 30000.00 }
    ],
    "average_booking_value": 3200.50
  }
}
```

### 📊 Recommended Visualizations
| Data Field | Chart Type | Description |
| :--- | :--- | :--- |
| `top_destinations` | **Word Cloud / Bar Chart** | Visualizes popular spots. |
| `top_packages` | **Leaderboard Table** | Ranked list showing Name, Bookings, and Revenue columns. |
| `average_booking_value` | **KPI Card** | currency value showing average ticket size. |

---

## 5. Team Performance
**Endpoint:** `/dashboard/performance/`

Returns user-level metrics for leaderboards.

### Request
```http
GET /dashboard/performance/?tour_operator_id=1
```

### Response
```json
{
  "status": "success",
  "data": {
    "performance_table": [
      {
        "agent": "alice",
        "leads_generated": 50,
        "bookings_closed": 10,
        "total_revenue": 100000.00,
        "conversion_rate": 20.0,
        "avg_booking_value": 10000.00
      },
      {
        "agent": "bob",
        "leads_generated": 30,
        "bookings_closed": 5,
        "total_revenue": 45000.00,
        "conversion_rate": 16.6,
        "avg_booking_value": 9000.00
      }
    ]
  }
}
```

### 📊 Recommended Visualizations
| Data Field | Chart Type | Description |
| :--- | :--- | :--- |
| `performance_table` | **Data Grid / Table** | Sortable table with columns for Agent, Leads, Bookings, Revenue, etc. |
| `performance_table` (Top Agent) | **Award/Badge Card** | Highlight the top agent (row 1) in a special "Employee of the Month" style widget. |

## Error Handling
All endpoints follow a standard error structure:
```json
{
  "status": "error",
  "message": "Error description here"
}
```
