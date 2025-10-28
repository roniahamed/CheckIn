# Data Models

## Overview

The CheckIn system uses three main models: `AccessToken`, `Patient`, and `QueueEntry`.

---

## AccessToken Model

### Description
Stores authentication tokens for different user roles (Form Manager, Doctor, Queue Manager).

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary key | Auto-generated |
| `token` | CharField | 8-digit access token | Max 100 chars, unique, auto-generated |
| `password` | CharField | Hashed password | Max 128 chars |
| `role` | CharField | User role | Max 20 chars, choices: 'form', 'doctor', 'queue' |
| `created_at` | DateTimeField | Creation timestamp | Auto-set on creation |
| `updated_at` | DateTimeField | Last update timestamp | Auto-updated |
| `is_active` | BooleanField | Token active status | Default: True |

### Role Choices

| Value | Display Name | Description |
|-------|--------------|-------------|
| `form` | Form | Can register patients |
| `doctor` | Doctor | Can manage consultations |
| `queue` | Queue | Can view queue |

### Methods

#### `set_password(raw_password)`
Hashes and sets the password.

**Parameters**:
- `raw_password` (string): Plain text password

**Example**:
```python
token = AccessToken.objects.create(role='form')
token.set_password('mypassword')
token.save()
```

#### `check_password(raw_password)`
Verifies a password against the stored hash.

**Parameters**:
- `raw_password` (string): Plain text password to verify

**Returns**: Boolean

**Example**:
```python
if token.check_password('mypassword'):
    print("Password is correct")
```

### Model Example

```python
{
  "id": 1,
  "token": "12345678",
  "password": "pbkdf2_sha256$...",  # Hashed
  "role": "form",
  "created_at": "2025-10-28T10:00:00Z",
  "updated_at": "2025-10-28T10:00:00Z",
  "is_active": true
}
```

---

## Patient Model

### Description
Stores comprehensive patient information including personal details, address, medical information, and status.

### Personal Information Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary key | Auto-generated |
| `fname` | CharField | Full name | Max 255 chars |
| `dob` | DateField | Date of birth | - |
| `gender` | CharField | Gender | Max 50 chars, choices |
| `pronoun` | CharField | Preferred pronoun | Max 50 chars, choices |
| `phone` | CharField | Phone number | Max 10 chars, 10 digits |
| `emergency_contact` | CharField | Emergency contact info | Max 255 chars |
| `ssn` | CharField | Social Security Number | Max 10 chars, 10 digits |

### Address Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `street1` | CharField | Street address line 1 | Max 255 chars |
| `street2` | CharField | Street address line 2 | Max 255 chars, optional |
| `last_known_address` | CharField | Last known address | Max 255 chars |
| `city` | CharField | City | Max 100 chars |
| `state` | CharField | State | Max 100 chars |
| `zip` | CharField | ZIP code | Max 10 chars, 5 digits |

### Medical & Insurance Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `medicaid_no` | CharField | Medicaid number | Max 12 chars, 10 digits, optional |
| `id_card` | CharField | Has valid ID? | Max 100 chars, choices |
| `insurance` | CharField | Insurance provider | Max 255 chars, choices |
| `race` | CharField | Race/ethnicity | Max 50 chars, choices |
| `pref_service_area` | CharField | Preferred service area | Max 255 chars, choices |

### Status Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `employed` | CharField | Employment status | Max 100 chars, choices, default: 'NO' |
| `shower` | CharField | Needs shower? | Max 100 chars, choices, default: 'No' |
| `hungry` | CharField | Is hungry? | Max 100 chars, choices, default: 'No' |
| `homeless` | CharField | Housing status | Max 100 chars, choices, default: 'Yes' |

### System Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `image` | ImageField | Patient photo | Upload to 'patient_images/', optional |
| `wait_time` | DurationField | Total wait time | Calculated, optional |
| `created_at` | DateTimeField | Creation timestamp | Auto-set on creation |
| `updated_at` | DateTimeField | Last update timestamp | Auto-updated |

### Field Choices

#### Gender Choices
- `male` - Male
- `female` - Female
- `other` - Other

#### Pronoun Choices
- `he/him` - He/Him
- `she/her` - She/Her

#### ID Card Choices
- `yes` - Yes
- `no` - No
- `lost/stolen` - LOST/STOLEN

#### Insurance Choices
- `humana` - Humana
- `aetna` - Aetna
- `magellan` - Magellan
- `anthem` - Anthem
- `sentara` - Sentara
- `united` - United

#### Race Choices
- `black_african_american` - Black/African American
- `caucasian` - Caucasian
- `hispanic_latino` - Hispanic/Latino
- `american_indian_or_alaskan_native` - American Indian or Alaskan Native
- `biracial` - Biracial
- `asian` - Asian
- `hawaiian_pacific_islander` - Hawaiian/Pacific Islander
- `other` - Other

#### Preferred Service Area Choices
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

#### Employment Choices
- `yes` - Yes
- `no` - No
- `disabled` - Disabled

#### Yes/No Choices (shower, hungry)
- `yes` - Yes
- `no` - No

#### Homeless Choices
- `yes` - Yes
- `no` - No
- `staying/someone` - Staying / Someone

### Model Example

```python
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
  "wait_time": "01:30:00",
  "created_at": "2025-10-28T10:30:00Z",
  "updated_at": "2025-10-28T12:00:00Z"
}
```

---

## QueueEntry Model

### Description
Represents a patient's position and status in the consultation queue.

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | AutoField | Primary key | Auto-generated |
| `patient` | OneToOneField | Related patient | Foreign key to Patient, cascade delete |
| `status` | CharField | Current queue status | Max 20 chars, choices |
| `check_in_time` | DateTimeField | Check-in timestamp | Default: now |
| `called_at` | DateTimeField | Called to consultation time | Optional |
| `check_out_time` | DateTimeField | Consultation end time | Optional |

### Status Choices

| Value | Display Name | Description |
|-------|--------------|-------------|
| `waiting` | Waiting | Patient in waiting queue |
| `in_consultation` | In Consultation | Patient currently with doctor |
| `completed` | Completed | Consultation finished |

### Relationships

- **Patient**: One-to-one relationship with Patient model
  - Related name: `queue_entry`
  - On delete: CASCADE (deletes queue entry when patient is deleted)

### Ordering

Queue entries are ordered by `check_in_time` (ascending) - first in, first out.

### Model Example

```python
{
  "id": 1,
  "patient": {
    "id": 1,
    "fname": "John Doe",
    "image": "/media/patient_images/john_doe_abc123.jpg"
  },
  "status": "waiting",
  "check_in_time": "2025-10-28T10:30:00Z",
  "called_at": null,
  "check_out_time": null
}
```

### Status Workflow

```
[Patient Check-in]
      ↓
  WAITING
      ↓
[Doctor Calls Next]
      ↓
IN_CONSULTATION
      ↓
[Doctor Completes]
      ↓
  COMPLETED
```

---

## Relationships Between Models

### AccessToken ←→ Patient
- No direct relationship
- AccessToken is used for authentication when creating patients

### Patient ←→ QueueEntry
- **One-to-One relationship**
- Each patient has exactly one queue entry
- Queue entry is created automatically when patient is registered
- Deleting a patient also deletes their queue entry

### Visual Schema

```
┌─────────────────┐
│  AccessToken    │
├─────────────────┤
│ id              │
│ token           │
│ password        │
│ role            │
│ is_active       │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌─────────────────┐         ┌─────────────────┐
│    Patient      │◄───────┤   QueueEntry    │
├─────────────────┤ 1:1    ├─────────────────┤
│ id              │         │ id              │
│ fname           │         │ patient_id      │
│ dob             │         │ status          │
│ gender          │         │ check_in_time   │
│ phone           │         │ called_at       │
│ ...             │         │ check_out_time  │
│ image           │         └─────────────────┘
│ wait_time       │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Database Queries

### Common Queries

#### Get all waiting patients
```python
waiting_patients = QueueEntry.objects.filter(
    status=QueueEntry.Status.WAITING
).select_related('patient').order_by('check_in_time')
```

#### Get next patient to call
```python
next_patient = QueueEntry.objects.filter(
    status=QueueEntry.Status.WAITING
).select_related('patient').first()
```

#### Get patient in consultation
```python
in_consultation = QueueEntry.objects.filter(
    status=QueueEntry.Status.IN_CONSULTATION
).select_related('patient')
```

#### Get active access tokens
```python
active_tokens = AccessToken.objects.filter(is_active=True)
```

#### Get today's patients
```python
from django.utils import timezone
from datetime import timedelta

today = timezone.now().date()
today_patients = Patient.objects.filter(
    created_at__date=today
)
```

---
*Last Updated: October 28, 2025*
