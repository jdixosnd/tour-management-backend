# Duplicate Package API Guide

This document outlines how to use the new API endpoint for duplicating tour packages.

## Endpoint Details

- **URL**: `/package/duplicate/`
- **Method**: `POST`
- **Content-Type**: `application/json`

## Request format

The request body must contain the `package_id` of the package you want to duplicate and the `tour_operator_id` (the current logged-in operator).

```json
{
    "package_id": "dcf7d7cc-1234-4567-8901-abcdef123456",
    "tour_operator_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `package_id` | String (UUID) | Yes | The UUID of the source package to copy. |
| `tour_operator_id` | String (UUID) | Yes | The UUID of the tour operator owning the package. |

## Response Format

### Success (201 Created)

Returns the new package details. The name will be prefixed with "Copy of ".

```json
{
    "message": "Package duplicated successfully",
    "package_id": "98765432-abcd-ef01-2345-67890abcdef1",
    "name": "Copy of Mystical Manali"
}
```

### Error Responses

**400 Bad Request** - Missing fields
```json
{
    "error": "package_id and tour_operator_id are required"
}
```

**403 Forbidden** - Package belongs to a different operator
```json
{
    "error": "Package does not belong to the specified tour operator."
}
```

**404 Not Found** - Package does not exist
```json
{
    "error": "Package not found"
}
```
