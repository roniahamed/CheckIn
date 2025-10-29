# API Specification v1.0

**Base URL**: `http://localhost:8000/api/`  
**Version**: 1.0  
**Last Updated**: October 28, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Login Endpoint](#1-login)
3. [Patient Endpoints](#2-patient-management)
4. [Doctor Endpoints](#3-doctor-management)
5. [Queue Endpoints](#4-queue-management)
6. [WebSocket Protocol](#5-websocket-protocol)
7. [Data Types](#6-data-types)
8. [Error Codes](#7-error-codes)

---

## Authentication

### Overview
The API uses JWT (JSON Web Token) authentication with a custom header.

### Custom Header
```
Roni-Authorization: Bearer <access_token>
```

### Token Lifetime
- **Access Token**: 60 minutes
- **Refresh Token**: 1 day

### Roles
- `form` - Form Manager (can register patients)
- `doctor` - Doctor (can manage consultations)
- `queue` - Queue Manager (can view queue)

---

## 1. Login

### POST `/api/login/`

Authenticate with token and password to receive JWT tokens.

**Authentication**: None required

#### Request

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "token": "string (8 digits, required)",
  "password": "string (required)"
}
```

#### Response

**Success (200 OK)**:
```json
{
  "refresh": "string (JWT refresh token)",
  "access": "string (JWT access token)",
  "role": "string (user role: 'form' | 'doctor' | 'queue')"
}
```

**Error (400 Bad Request)**:
```json
{
  "error": "Please provide both token and password."
}
```

**Error (401 Unauthorized)**:
```json
{
  "error": "Invalid credentials or inactive token."
}
```

#### Example

**Request**:
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"token":"12345678","password":"mypassword"}'
```

**Response**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "form"
}
```

---

## 2. Patient Management

### POST `/api/patients/`

Register a new patient and add to queue.

**Authentication**: Required (Form Manager role)

#### Request

**Headers**:
```http
Roni-Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body** (all fields required unless marked optional):

| Field | Type | Constraints | Required |
|-------|------|-------------|----------|
| fname | string | Max 255 chars | Yes |
| dob | date | YYYY-MM-DD, not future | Yes |
| gender | string | 'male' \| 'female' \| 'non_binary' \| 'other' | Yes |
| pronoun | string | 'he_him' \| 'she_her' \| 'they_them' \| 'other' | Yes |
| phone | string | 10 digits | Yes |
| emergency_contact | string | Max 255 chars | Yes |
| ssn | string | 10 digits | Yes |
| street1 | string | Max 255 chars | Yes |
| street2 | string | Max 255 chars | No |
| last_known_address | string | Max 255 chars | Yes |
| city | string | Max 100 chars | Yes |
| state | string | 'VA' \| 'MD' \| 'NC' \| 'SC' | Yes |
| zip | string | 5 digits | Yes |
| medicaid_no | string | 10 digits | No |
| id_card | string | 'yes' \| 'no' \| 'lost' | Yes |
| insurance | string | See [Insurance Choices](#insurance-choices) | Yes |
| race | string | See [Race Choices](#race-choices) | Yes |
| pref_service_area | string | See [Service Area Choices](#service-area-choices) | Yes |
| employed | string | 'yes' \| 'no' \| 'disabled' \| 'retired' | Yes |
| shower | string | 'yes' \| 'no' | Yes |
| hungry | string | 'yes' \| 'no' | Yes |
| homeless | string | 'yes' \| 'no' | Yes |
| image | file | JPEG/PNG, max 5MB | No |

#### Response

**Success (201 Created)**:
```json
{
  "id": "integer",
  "fname": "string",
  "dob": "date",
  "gender": "string",
  "pronoun": "string",
  "phone": "string",
  "emergency_contact": "string",
  "ssn": "string",
  "street1": "string",
  "street2": "string | null",
  "last_known_address": "string",
  "city": "string",
  "state": "string",
  "zip": "string",
  "medicaid_no": "string | null",
  "id_card": "string",
  "insurance": "string",
  "race": "string",
  "pref_service_area": "string",
  "employed": "string",
  "shower": "string",
  "hungry": "string",
  "homeless": "string",
  "image": "string (URL) | null",
  "wait_time": "duration | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error (400 Bad Request)**:
```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

**Error (401 Unauthorized)**: See [Authentication Errors](#authentication-errors)

**Error (403 Forbidden)**:
```json
{
  "detail": "Access Denied: You must have the 'form' role to access this resource."
}
```

#### Side Effects
1. Creates new Patient record
2. Creates QueueEntry with status 'waiting'
3. Sends WebSocket event `PATIENT_ADDED`
4. Triggers async email notification

---

### GET `/api/patients/`

Get welcome message (for testing authentication).

**Authentication**: Required (Form Manager role)

#### Response

**Success (200 OK)**:
```json
{
  "message": "Welcome Form User (Token: 12345678)! You can access the patient form."
}
```

---

## 3. Doctor Management

### POST `/api/doctors/`

Manage patient consultations.

**Authentication**: Required (Doctor role)

#### Call Next Patient

**Request Body**:
```json
{
  "action": "call_next"
}
```

**Success Response (200 OK)**:
```json
{
  "message": "Action successful.",
  "patient": {
    "id": "integer",
    "fname": "string",
    "status": "in_consultation",
    "image": "string (URL) | null"
  }
}
```

**Error (404 Not Found)**:
```json
{
  "error": "No patients in the waiting."
}
```

**Side Effects**:
1. Updates first waiting QueueEntry to 'in_consultation'
2. Sets `called_at` timestamp
3. Sends WebSocket event `PATIENT_CALLED`

#### Complete Consultation

**Request Body**:
```json
{
  "action": "complete",
  "patient_id": "integer"
}
```

**Success Response (200 OK)**:
```json
{
  "message": "Action successful.",
  "patient": {
    "id": "integer",
    "fname": "string",
    "status": "completed",
    "image": "string (URL) | null"
  }
}
```

**Error (400 Bad Request)**:
```json
{
  "error": "Patient is not currently in progress."
}
```

**Side Effects**:
1. Updates QueueEntry to 'completed'
2. Sets `check_out_time` timestamp
3. Calculates and stores wait time
4. Sends WebSocket event `PATIENT_COMPLETED`

---

### GET `/api/doctors/`

Get welcome message (for testing authentication).

**Authentication**: Required (Doctor role)

#### Response

**Success (200 OK)**:
```json
{
  "message": "Welcome Doctor (Token: 87654321)! You can access the doctor patient management."
}
```

---

## 4. Queue Management

### GET `/api/queue/`

Get current queue with waiting and in-consultation patients.

**Authentication**: None (currently)

#### Response

**Success (200 OK)**:
```json
[
  {
    "id": "integer",
    "patient": {
      "id": "integer",
      "fname": "string",
      "image": "string (URL) | null"
    },
    "status": "waiting | in_consultation",
    "check_in_time": "datetime (ISO 8601)"
  }
]
```

---

## 5. WebSocket Protocol

### Connection

**URL**: `ws://localhost:8000/ws/queue/`

**Protocol**: WebSocket

### Events

All events follow this structure:

```json
{
  "type": "send.queue.update",
  "event": "PATIENT_ADDED | PATIENT_CALLED | PATIENT_COMPLETED",
  "patient": {
    "id": "integer",
    "fname": "string",
    "status": "waiting | in_consultation | completed",
    "image": "string (URL) | null"
  }
}
```

#### Event Types

| Event | Trigger | Patient Status |
|-------|---------|----------------|
| PATIENT_ADDED | POST /api/patients/ | waiting |
| PATIENT_CALLED | POST /api/doctors/ (call_next) | in_consultation |
| PATIENT_COMPLETED | POST /api/doctors/ (complete) | completed |

---

## 6. Data Types

### Date Format
ISO 8601: `YYYY-MM-DD`

Example: `2025-10-28`

### DateTime Format
ISO 8601: `YYYY-MM-DDTHH:MM:SSZ`

Example: `2025-10-28T10:30:00Z`

### Duration Format
PostgreSQL interval: `HH:MM:SS`

Example: `01:30:00` (1 hour 30 minutes)

### Insurance Choices
- `humana` - Humana
- `aetna` - Aetna
- `magellan` - Magellan
- `anthem` - Anthem
- `sentara` - Sentara
- `united` - United
- `dont_know` - I Don't Know

### Race Choices
- `black_african_american` - Black/African American
- `caucasian` - Caucasian
- `hispanic_latino` - Hispanic/Latino
- `american_indian_alaskan_native` - American Indian or Alaskan Native
- `biracial` - Biracial
- `asian` - Asian
- `middle_eastern` - Middle Eastern
- `hawaiian_pacific_islander` - Hawaiian/Pacific Islander
- `other` - Other

### Service Area Choices
- `petersburg` - Petersburg
- `east_end` - East End
- `west_end` - West End
- `chesterfield` - Chesterfield
- `chester` - Chester
- `colonial_heights` - Colonial Heights
- `north_side_richmond` - North side Richmond
- `southside_richmond` - Southside Richmond
- `church_hill` - Church Hill
- `ashland` - Ashland
- `hopewell` - Hopewell

---

## 7. Error Codes

### HTTP Status Codes

| Code | Name | Description |
|------|------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Authentication Errors

**401 - Missing Credentials**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**401 - Invalid Token**:
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**401 - User Not Found**:
```json
{
  "detail": "User not found or inactive.",
  "code": "user_not_found"
}
```

### Permission Errors

**403 - Insufficient Role**:
```json
{
  "detail": "Access Denied: You must have the '{role}' role to access this resource."
}
```

### Validation Errors

**400 - Field Validation**:
```json
{
  "field_name": [
    "Error message describing the validation failure"
  ]
}
```

Common validation messages:
- `"This field is required."`
- `"This field may not be blank."`
- `"Phone number must be a 10-digit number."`
- `"SSN must be a 10-digit number."`
- `"ZIP code must be a 5-digit number."`
- `"Date of birth cannot be in the future."`
- `"Image size should not exceed 5 MB."`
- `"Unsupported image type. Only JPEG and PNG are allowed."`

---

## Testing

### Health Check

You can test if the API is running:

```bash
curl http://localhost:8000/admin/
# Should return HTML (Django admin page)
```

### Authentication Test

```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"token":"12345678","password":"test"}'

# Use returned token
curl -X GET http://localhost:8000/api/patients/ \
  -H "Roni-Authorization: Bearer <access_token>"
```

---

## Rate Limiting

Currently not implemented. Consider implementing for production.

## Versioning

Current version: **1.0**

API versioning is not currently implemented. Future versions may use URL versioning (e.g., `/api/v2/`).

---

*API Specification v1.0 - Last Updated: October 30, 2025*
