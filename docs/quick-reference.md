# Quick Reference Guide

## API Endpoints Summary

### Authentication

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/login/` | POST | No | Login with token and password |

### Patient Management (Form Manager)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/patients/` | POST | Yes (Form) | Register new patient |
| `/api/patients/` | GET | Yes (Form) | Get welcome message |

### Doctor Management (Doctor)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/doctors/` | POST | Yes (Doctor) | Call next or complete consultation |
| `/api/doctors/` | GET | Yes (Doctor) | Get welcome message |

### Queue Management

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/queue/` | GET | No* | Get current queue |

*Permissions currently commented out

---

## Authentication Header

All authenticated endpoints require:

```
Roni-Authorization: Bearer <access_token>
```

---

## Patient Model Fields

### Required Fields

| Field | Type | Format/Choices |
|-------|------|----------------|
| `fname` | string | Max 255 chars |
| `dob` | date | YYYY-MM-DD |
| `gender` | string | `male`, `female`, `other` |
| `pronoun` | string | `he/him`, `she/her` |
| `phone` | string | 10 digits |
| `emergency_contact` | string | Max 255 chars |
| `ssn` | string | 10 digits |
| `street1` | string | Max 255 chars |
| `last_known_address` | string | Max 255 chars |
| `city` | string | Max 100 chars |
| `state` | string | Max 100 chars |
| `zip` | string | 5 digits |
| `id_card` | string | `yes`, `no`, `lost/stolen` |
| `insurance` | string | `humana`, `aetna`, `magellan`, `anthem`, `sentara`, `united` |
| `race` | string | See [Data Models](data-models.md) |
| `pref_service_area` | string | See [Data Models](data-models.md) |
| `employed` | string | `yes`, `no`, `disabled` |
| `shower` | string | `yes`, `no` |
| `hungry` | string | `yes`, `no` |
| `homeless` | string | `yes`, `no`, `staying/someone` |

### Optional Fields

| Field | Type | Format/Constraints |
|-------|------|-------------------|
| `street2` | string | Max 255 chars |
| `medicaid_no` | string | 10 digits |
| `image` | file | JPEG/PNG, max 5MB |

---

## Doctor Actions

### Call Next Patient

```json
{
  "action": "call_next"
}
```

### Complete Consultation

```json
{
  "action": "complete",
  "patient_id": 1
}
```

---

## WebSocket Events

### Connection

```
ws://localhost:8000/ws/queue/
```

### Event Types

| Event | Trigger | Status |
|-------|---------|--------|
| `PATIENT_ADDED` | Patient check-in | `waiting` |
| `PATIENT_CALLED` | Doctor calls next | `in_consultation` |
| `PATIENT_COMPLETED` | Consultation done | `completed` |

### Event Structure

```json
{
  "type": "send.queue.update",
  "event": "PATIENT_ADDED",
  "patient": {
    "id": 1,
    "fname": "John Doe",
    "status": "waiting",
    "image": "/media/patient_images/..."
  }
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (auth required) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Server Error |

---

## Common Validation Rules

| Field | Validation |
|-------|-----------|
| Phone | Exactly 10 digits |
| SSN | Exactly 10 digits |
| ZIP | Exactly 5 digits |
| Medicaid No | Exactly 10 digits |
| DOB | Not in future |
| Image | JPEG/PNG, max 5MB |

---

## Quick Start Commands

### Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"token":"12345678","password":"mypass"}'
```

### Check-in Patient
```bash
curl -X POST http://localhost:8000/api/patients/ \
  -H "Roni-Authorization: Bearer <token>" \
  -F "fname=John Doe" \
  -F "dob=1990-01-01" \
  -F "gender=male" \
  -F "pronoun=he/him" \
  # ... (add all required fields)
```

### Call Next Patient
```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action":"call_next"}'
```

### Complete Consultation
```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action":"complete","patient_id":1}'
```

### Get Queue
```bash
curl -X GET http://localhost:8000/api/queue/
```

---

## Environment Variables

Essential `.env` configuration:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
SITE_URL=http://localhost:9000
SITE_DOMAIN=http://localhost:8000
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## Running the System

```bash
# 1. Start Redis
redis-server

# 2. Start Celery (new terminal)
celery -A CheckIn worker -l info

# 3. Start ASGI Server with Daphne (new terminal)
daphne -b 0.0.0.0 -p 8000 CheckIn.asgi:application

# 4. Access API
# API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
# WebSocket: ws://localhost:8000/ws/queue/
```

---



## Access Token Roles

| Role | Value | Can Access |
|------|-------|------------|
| Form Manager | `form` | Patient registration |
| Doctor | `doctor` | Patient consultations |
| Queue Manager | `queue` | Queue viewing |

---

## Data Flow

```
1. Patient Check-in (Form Manager)
   ↓
2. Queue Entry Created (status: waiting)
   ↓
3. WebSocket Event (PATIENT_ADDED)
   ↓
4. Email Notification Sent
   ↓
5. Doctor Calls Next (status: in_consultation)
   ↓
6. WebSocket Event (PATIENT_CALLED)
   ↓
7. Doctor Completes (status: completed)
   ↓
8. WebSocket Event (PATIENT_COMPLETED)
   ↓
9. Wait Time Calculated
```

---

## Troubleshooting

### Cannot connect to API
- Check ASGI server is running: `daphne -b 0.0.0.0 -p 8000 CheckIn.asgi:application`
- Verify URL: `http://localhost:8000/api/`

### Authentication errors
- Ensure token is active in admin panel
- Check header format: `Roni-Authorization: Bearer <token>`
- Verify token hasn't expired

### WebSocket not connecting
- Check Django Channels is running
- Verify Redis is running: `redis-cli ping` should return `PONG`
- Check WebSocket URL: `ws://localhost:8000/ws/queue/`

### Redis "Address already in use" error
- Redis is already running, no need to start it again
- Check if Redis is running: `redis-cli ping`
- If you need to restart Redis:
  ```bash
  # Find Redis process
  ps aux | grep redis-server
  # Kill the process (replace PID with actual process ID)
  kill <PID>
  # Then start Redis again
  redis-server
  ```

### Email not sending
- Check Celery worker is running
- Verify email configuration in `.env`
- Check Celery logs for errors

### Image upload fails
- Ensure image is JPEG or PNG
- Check file size is under 5MB
- Verify MEDIA_ROOT directory exists and is writable

---

*Last Updated: October 29, 2025*
