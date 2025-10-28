# API Endpoints

## Base URL
```
http://localhost:8000/api/
```

## Endpoints Overview

| Endpoint | Method | Role Required | Description |
|----------|--------|---------------|-------------|
| `/api/login/` | POST | None | Authenticate and get JWT tokens |
| `/api/patients/` | POST | Form Manager | Register a new patient |
| `/api/patients/` | GET | Form Manager | Get welcome message |
| `/api/doctors/` | POST | Doctor | Manage patient consultations |
| `/api/doctors/` | GET | Doctor | Get welcome message |
| `/api/queue/` | GET | None* | Get current queue status |

*Note: Queue endpoint currently has permissions commented out

---

## 1. Login

### Authenticate User

**Endpoint**: `POST /api/login/`

**Description**: Authenticate using token and password to receive JWT tokens.

**Authentication**: None required

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "token": "12345678",
  "password": "your-password"
}
```

**Field Descriptions**:
- `token` (string, required): 8-digit access token
- `password` (string, required): Access token password

**Success Response** (200 OK):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "role": "form"
}
```

**Error Responses**:

- **400 Bad Request**:
```json
{
  "error": "Please provide both token and password."
}
```

- **401 Unauthorized**:
```json
{
  "error": "Invalid credentials or inactive token."
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "12345678",
    "password": "mypassword"
  }'
```

---

## 2. Patient Management

### 2.1 Create Patient (Check-In)

**Endpoint**: `POST /api/patients/`

**Description**: Register a new patient and add them to the queue. Sends email notification and WebSocket update.

**Authentication**: Required (Form Manager role)

**Request Headers**:
```
Roni-Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body** (multipart/form-data):

All fields except `street2`, `medicaid_no`, and `image` are required.

```json
{
  "fname": "John Doe",
  "dob": "1990-05-15",
  "gender": "male",
  "pronoun": "he/him",
  "phone": "5551234567",
  "emergency_contact": "Jane Doe - 5559876543",
  "ssn": "1234567890",
  "street1": "123 Main Street",
  "street2": "Apt 4B",
  "last_known_address": "123 Main Street, Apt 4B",
  "city": "Richmond",
  "state": "VA",
  "zip": "23219",
  "medicaid_no": "1234567890",
  "id_card": "yes",
  "insurance": "humana",
  "race": "caucasian",
  "pref_service_area": "east_end",
  "employed": "yes",
  "shower": "no",
  "hungry": "yes",
  "homeless": "no",
  "image": <file>
}
```

**Field Specifications**:

| Field | Type | Required | Constraints | Choices |
|-------|------|----------|-------------|---------|
| `fname` | string | Yes | Max 255 chars | - |
| `dob` | date | Yes | YYYY-MM-DD, not future | - |
| `gender` | string | Yes | - | `male`, `female`, `other` |
| `pronoun` | string | Yes | - | `he/him`, `she/her` |
| `phone` | string | Yes | 10 digits | - |
| `emergency_contact` | string | Yes | Max 255 chars | - |
| `ssn` | string | Yes | 10 digits | - |
| `street1` | string | Yes | Max 255 chars | - |
| `street2` | string | No | Max 255 chars | - |
| `last_known_address` | string | Yes | Max 255 chars | - |
| `city` | string | Yes | Max 100 chars | - |
| `state` | string | Yes | Max 100 chars | - |
| `zip` | string | Yes | 5 digits | - |
| `medicaid_no` | string | No | 10 digits | - |
| `id_card` | string | Yes | - | `yes`, `no`, `lost/stolen` |
| `insurance` | string | Yes | - | `humana`, `aetna`, `magellan`, `anthem`, `sentara`, `united` |
| `race` | string | Yes | - | `black_african_american`, `caucasian`, `hispanic_latino`, `american_indian_or_alaskan_native`, `biracial`, `asian`, `hawaiian_pacific_islander`, `other` |
| `pref_service_area` | string | Yes | - | `east_end`, `west_end`, `chesterfield`, `chester`, `colonial_heights`, `north_side_richmond`, `southside_richmond`, `church_hill`, `ashland`, `hopewell` |
| `employed` | string | Yes | - | `yes`, `no`, `disabled` |
| `shower` | string | Yes | - | `yes`, `no` |
| `hungry` | string | Yes | - | `yes`, `no` |
| `homeless` | string | Yes | - | `yes`, `no`, `staying/someone` |
| `image` | file | No | JPEG/PNG, max 5MB | - |

**Success Response** (201 Created):
```json
{
  "id": 1,
  "fname": "John Doe",
  "dob": "1990-05-15",
  "gender": "male",
  "pronoun": "he/him",
  "phone": "5551234567",
  "emergency_contact": "Jane Doe - 5559876543",
  "ssn": "1234567890",
  "street1": "123 Main Street",
  "street2": "Apt 4B",
  "last_known_address": "123 Main Street, Apt 4B",
  "city": "Richmond",
  "state": "VA",
  "zip": "23219",
  "medicaid_no": "1234567890",
  "id_card": "yes",
  "insurance": "humana",
  "race": "caucasian",
  "pref_service_area": "east_end",
  "employed": "yes",
  "shower": "no",
  "hungry": "yes",
  "homeless": "no",
  "image": "/media/patient_images/john_doe_abc123.jpg",
  "wait_time": null,
  "created_at": "2025-10-28T10:30:00Z",
  "updated_at": "2025-10-28T10:30:00Z"
}
```

**Error Responses**:

- **400 Bad Request** - Validation errors:
```json
{
  "fname": ["This field may not be blank."],
  "phone": ["Phone number must be a 10-digit number."],
  "ssn": ["SSN must be a 10-digit number."],
  "dob": ["Date of birth cannot be in the future."],
  "image": ["Image size should not exceed 5 MB."]
}
```

- **401 Unauthorized**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **403 Forbidden**:
```json
{
  "detail": "Access Denied: You must have the 'form' role to access this resource."
}
```

**Side Effects**:
1. Creates a new `QueueEntry` with status 'waiting'
2. Sends WebSocket event `PATIENT_ADDED` to `queue_group`
3. Triggers async email notification to administrators

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/patients/ \
  -H "Roni-Authorization: Bearer <access_token>" \
  -F "fname=John Doe" \
  -F "dob=1990-05-15" \
  -F "gender=male" \
  -F "pronoun=he/him" \
  -F "phone=5551234567" \
  -F "emergency_contact=Jane Doe - 5559876543" \
  -F "ssn=1234567890" \
  -F "street1=123 Main Street" \
  -F "street2=Apt 4B" \
  -F "last_known_address=123 Main Street, Apt 4B" \
  -F "city=Richmond" \
  -F "state=VA" \
  -F "zip=23219" \
  -F "medicaid_no=1234567890" \
  -F "id_card=yes" \
  -F "insurance=humana" \
  -F "race=caucasian" \
  -F "pref_service_area=east_end" \
  -F "employed=yes" \
  -F "shower=no" \
  -F "hungry=yes" \
  -F "homeless=no" \
  -F "image=@/path/to/photo.jpg"
```

### 2.2 Get Patient Form Access

**Endpoint**: `GET /api/patients/`

**Description**: Returns a welcome message for form managers.

**Authentication**: Required (Form Manager role)

**Request Headers**:
```
Roni-Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
  "message": "Welcome Form User (Token: 12345678)! You can access the patient form."
}
```

---

## 3. Doctor Management

### 3.1 Call Next Patient

**Endpoint**: `POST /api/doctors/`

**Description**: Call the next patient in the waiting queue to consultation.

**Authentication**: Required (Doctor role)

**Request Headers**:
```
Roni-Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "action": "call_next"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Action successful.",
  "patient": {
    "id": 1,
    "fname": "John Doe",
    "status": "in_consultation",
    "image": "/media/patient_images/john_doe_abc123.jpg"
  }
}
```

**Error Responses**:

- **404 Not Found** - No waiting patients:
```json
{
  "error": "No patients in the waiting."
}
```

- **500 Internal Server Error** - Processing error:
```json
{
  "error": "Could not process the request. Please try again."
}
```

**Side Effects**:
1. Updates queue entry status to `in_consultation`
2. Sets `called_at` timestamp
3. Sends WebSocket event `PATIENT_CALLED` to `queue_group`

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "call_next"
  }'
```

### 3.2 Complete Patient Consultation

**Endpoint**: `POST /api/doctors/`

**Description**: Mark a patient's consultation as complete.

**Authentication**: Required (Doctor role)

**Request Headers**:
```
Roni-Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "action": "complete",
  "patient_id": 1
}
```

**Field Descriptions**:
- `action` (string, required): Must be "complete"
- `patient_id` (integer, required): ID of the patient to complete

**Success Response** (200 OK):
```json
{
  "message": "Action successful.",
  "patient": {
    "id": 1,
    "fname": "John Doe",
    "status": "completed",
    "image": "/media/patient_images/john_doe_abc123.jpg"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Invalid action or patient:
```json
{
  "error": "Invalid action or missing patient."
}
```

- **400 Bad Request** - Patient not in consultation:
```json
{
  "error": "Patient is not currently in progress."
}
```

**Side Effects**:
1. Updates queue entry status to `completed`
2. Sets `check_out_time` timestamp
3. Calculates and stores wait time for the patient
4. Sends WebSocket event `PATIENT_COMPLETED` to `queue_group`

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "complete",
    "patient_id": 1
  }'
```

### 3.3 Get Doctor Access

**Endpoint**: `GET /api/doctors/`

**Description**: Returns a welcome message for doctors.

**Authentication**: Required (Doctor role)

**Request Headers**:
```
Roni-Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
  "message": "Welcome Doctor (Token: 87654321)! You can access the doctor patient management."
}
```

---

## 4. Queue Management

### 4.1 Get Queue Status

**Endpoint**: `GET /api/queue/`

**Description**: Retrieve the current patient queue with waiting and in-consultation patients.

**Authentication**: None (permissions currently commented out)

**Request Headers**:
```
Content-Type: application/json
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "patient": {
      "id": 1,
      "fname": "John Doe",
      "image": "/media/patient_images/john_doe_abc123.jpg"
    },
    "status": "waiting",
    "check_in_time": "2025-10-28T10:30:00Z"
  },
  {
    "id": 2,
    "patient": {
      "id": 2,
      "fname": "Jane Smith",
      "image": "/media/patient_images/jane_smith_def456.jpg"
    },
    "status": "in_consultation",
    "check_in_time": "2025-10-28T10:25:00Z"
  }
]
```

**Response Fields**:
- `id` (integer): Queue entry ID
- `patient` (object): Patient information
  - `id` (integer): Patient ID
  - `fname` (string): Patient full name
  - `image` (string|null): Patient photo URL
- `status` (string): Current status (`waiting` or `in_consultation`)
- `check_in_time` (datetime): When patient checked in

**cURL Example**:
```bash
curl -X GET http://localhost:8000/api/queue/ \
  -H "Content-Type: application/json"
```

---

## Common Response Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK | Request successful |
| 201 Created | Resource created successfully |
| 400 Bad Request | Invalid request data or validation errors |
| 401 Unauthorized | Missing or invalid authentication |
| 403 Forbidden | Insufficient permissions for the resource |
| 404 Not Found | Resource not found |
| 500 Internal Server Error | Server error occurred |

## Rate Limiting

Currently, there is no rate limiting implemented. Consider implementing rate limiting for production use.

## CORS Configuration

The API allows CORS requests from:
- `http://localhost:8001`
- `http://127.0.0.1:8001`
- `http://localhost:3000`
- `http://127.0.0.1:3000`

All headers are allowed (`*`).

---
*Last Updated: October 28, 2025*
