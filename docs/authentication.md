# Authentication

## Overview

The CheckIn API uses **JWT (JSON Web Token)** authentication with a custom token-based system. Each user is assigned a unique 8-digit token and password, along with a specific role that determines their access permissions.

## Roles

The system supports three distinct roles:

| Role | Key | Description |
|------|-----|-------------|
| Form Manager | `form` | Can register and check-in patients |
| Doctor | `doctor` | Can manage patient consultations and queue |
| Queue Manager | `queue` | Can view the patient queue |

## Authentication Flow

### 1. Login Endpoint

**Endpoint**: `POST /api/login/`

**Description**: Authenticate with token and password to receive JWT tokens.

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

**Success Response** (200 OK):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "form"
}
```

**Error Responses**:

- **400 Bad Request** - Missing credentials:
```json
{
  "error": "Please provide both token and password."
}
```

- **401 Unauthorized** - Invalid credentials:
```json
{
  "error": "Invalid credentials or inactive token."
}
```

### 2. Using Access Token

After successful login, include the access token in the **custom header** `Roni-Authorization` for all subsequent requests.

**Request Headers**:
```
Roni-Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**Example**:
```bash
curl -X GET http://localhost:8000/api/patients/ \
  -H "Roni-Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json"
```

### 3. Token Refresh

When the access token expires (default: 60 minutes), use the refresh token to obtain a new access token.

**Note**: Token refresh endpoint is provided by `simplejwt` library. You may need to add it to your URLs if not already configured:

```python
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # ... other patterns
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

**Endpoint**: `POST /api/token/refresh/`

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Token Expiration

| Token Type | Lifetime |
|------------|----------|
| Access Token | 60 minutes |
| Refresh Token | 1 day |

## Permission Classes

Different endpoints require different roles:

### IsFormManager
- **Required Role**: `form`
- **Endpoints**: 
  - `POST /api/patients/` - Create patient

### IsDoctor
- **Required Role**: `doctor`
- **Endpoints**:
  - `POST /api/doctors/` - Manage patient consultations

### IsQueueManager
- **Required Role**: `queue`
- **Endpoints**:
  - `GET /api/queue/` - View queue (currently commented out in code)

## Error Handling

### Authentication Errors

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**401 Unauthorized** - Token expired:
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

### Permission Errors

**403 Forbidden** - Insufficient permissions:
```json
{
  "detail": "Access Denied: You must have the 'form' role to access this resource."
}
```

## Creating Access Tokens

Access tokens are created through the Django admin panel:

1. Log in to `/admin/`
2. Navigate to **Management** → **Access Tokens**
3. Click **Add Access Token**
4. Fill in the details:
   - **Token**: Auto-generated (8 digits)
   - **Password**: Enter password (will be hashed)
   - **Role**: Select from dropdown
   - **Is Active**: Check to enable

**Programmatic Creation** (Python shell):
```python
from management.models import AccessToken

# Create a new access token
token = AccessToken.objects.create(role='form')
token.set_password('secure-password')
token.save()

print(f"Token: {token.token}")
print(f"Password: secure-password")
print(f"Role: {token.role}")
```

## Security Best Practices

1. **Store tokens securely**: Never expose tokens in client-side code
2. **Use HTTPS**: Always use HTTPS in production
3. **Rotate tokens**: Regularly update passwords and deactivate old tokens
4. **Monitor activity**: Track token usage through the admin panel
5. **Set strong passwords**: Use complex passwords for all access tokens

## Example Authentication Workflow

### Step 1: Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"token": "12345678", "password": "mypassword"}'
```

### Step 2: Store Tokens
```javascript
// JavaScript example
const response = await fetch('http://localhost:8000/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token: '12345678', password: 'mypassword' })
});

const data = await response.json();
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
localStorage.setItem('role', data.role);
```

### Step 3: Make Authenticated Requests
```javascript
const accessToken = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/patients/', {
  method: 'GET',
  headers: {
    'Roni-Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

---
*Last Updated: October 28, 2025*
