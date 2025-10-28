# Error Handling

## Overview

The CheckIn API uses standard HTTP status codes and provides detailed error messages to help you identify and fix issues.

## HTTP Status Codes

| Status Code | Meaning | When It Occurs |
|-------------|---------|----------------|
| 200 OK | Success | Successful GET or action request |
| 201 Created | Created | Successfully created a new resource |
| 400 Bad Request | Client Error | Invalid request data or validation failure |
| 401 Unauthorized | Authentication Error | Missing or invalid authentication credentials |
| 403 Forbidden | Permission Error | Authenticated but lacks required permissions |
| 404 Not Found | Not Found | Requested resource doesn't exist |
| 500 Internal Server Error | Server Error | Unexpected server error |

---

## Authentication Errors

### 401 Unauthorized - Missing Credentials

**Occurs when**: Request doesn't include authentication header

**Response**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution**: Include the `Roni-Authorization` header with your JWT token
```
Roni-Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 401 Unauthorized - Invalid Token

**Occurs when**: JWT token is malformed, expired, or invalid

**Response**:
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Solutions**:
1. Check if token is properly formatted
2. Refresh the token if expired
3. Login again to get a new token

### 401 Unauthorized - Invalid Login Credentials

**Occurs when**: Login credentials are incorrect or token is inactive

**Response**:
```json
{
  "error": "Invalid credentials or inactive token."
}
```

**Solutions**:
1. Verify the token and password are correct
2. Check if the token is active in the admin panel
3. Ensure you're using the correct token-password combination

### 401 Unauthorized - User Not Found

**Occurs when**: Token in JWT doesn't correspond to an active user

**Response**:
```json
{
  "detail": "User not found or inactive.",
  "code": "user_not_found"
}
```

**Solution**: The access token may have been deleted or deactivated. Login again with valid credentials.

---

## Permission Errors

### 403 Forbidden - Insufficient Role

**Occurs when**: User is authenticated but doesn't have the required role

**Response Examples**:

For Form Manager endpoints:
```json
{
  "detail": "Access Denied: You must have the 'form' role to access this resource."
}
```

For Doctor endpoints:
```json
{
  "detail": "Access Denied: You must have the 'doctor' role to access this resource."
}
```

For Queue Manager endpoints:
```json
{
  "detail": "Access Denied: You must have the 'queue' role to access this resource."
}
```

**Solution**: Use an access token with the appropriate role for the endpoint you're trying to access.

---

## Validation Errors

### 400 Bad Request - Missing Required Fields

**Occurs when**: Required fields are missing from the request

**Response Example**:
```json
{
  "fname": ["This field is required."],
  "dob": ["This field is required."],
  "phone": ["This field is required."]
}
```

**Solution**: Include all required fields in your request.

### 400 Bad Request - Field Validation Errors

**Occurs when**: Field values don't meet validation requirements

**Response Examples**:

Invalid phone number:
```json
{
  "phone": ["Phone number must be a 10-digit number."]
}
```

Invalid SSN:
```json
{
  "ssn": ["SSN must be a 10-digit number."]
}
```

Invalid ZIP code:
```json
{
  "zip": ["ZIP code must be a 5-digit number."]
}
```

Invalid Medicaid number:
```json
{
  "medicaid_no": ["Medicaid number must be a 10-digit number."]
}
```

Future date of birth:
```json
{
  "dob": ["Date of birth cannot be in the future."]
}
```

Invalid image type:
```json
{
  "image": ["Unsupported image type. Only JPEG and PNG are allowed."]
}
```

Image too large:
```json
{
  "image": ["Image size should not exceed 5 MB."]
}
```

Invalid choice:
```json
{
  "gender": ["Invalid choice. Available options are: male, female, other."]
}
```

**Solution**: Ensure field values meet the validation requirements specified in the [Data Models](data-models.md) documentation.

### 400 Bad Request - Missing Login Fields

**Occurs when**: Token or password is missing from login request

**Response**:
```json
{
  "error": "Please provide both token and password."
}
```

**Solution**: Include both `token` and `password` in the request body.

### 400 Bad Request - Invalid Action

**Occurs when**: Invalid or missing action for doctor endpoints

**Response**:
```json
{
  "error": "Invalid action or missing patient."
}
```

**Solution**: Ensure the action is either "call_next" or "complete", and include `patient_id` for the "complete" action.

### 400 Bad Request - Patient Not in Consultation

**Occurs when**: Trying to complete a patient who isn't currently in consultation

**Response**:
```json
{
  "error": "Patient is not currently in progress."
}
```

**Solution**: Only complete patients who have been called to consultation.

---

## Resource Not Found Errors

### 404 Not Found - No Waiting Patients

**Occurs when**: Doctor tries to call next patient but queue is empty

**Response**:
```json
{
  "error": "No patients in the waiting."
}
```

**Solution**: Wait for patients to check in before calling the next patient.

---

## Server Errors

### 500 Internal Server Error

**Occurs when**: Unexpected server error during request processing

**Response**:
```json
{
  "error": "Could not process the request. Please try again."
}
```

**Solution**: 
1. Try the request again
2. Check server logs for details
3. Contact system administrator if the issue persists

---

## Common Error Scenarios

### Scenario 1: Creating Patient with Invalid Data

**Request**:
```bash
curl -X POST http://localhost:8000/api/patients/ \
  -H "Roni-Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "fname": "John Doe",
    "phone": "123",
    "dob": "2030-01-01"
  }'
```

**Response** (400 Bad Request):
```json
{
  "phone": ["Phone number must be a 10-digit number."],
  "dob": ["Date of birth cannot be in the future."],
  "gender": ["This field is required."],
  "pronoun": ["This field is required."],
  "emergency_contact": ["This field is required."],
  "ssn": ["This field is required."],
  "street1": ["This field is required."],
  "last_known_address": ["This field is required."],
  "city": ["This field is required."],
  "state": ["This field is required."],
  "zip": ["This field is required."],
  "id_card": ["This field is required."],
  "insurance": ["This field is required."],
  "race": ["This field is required."],
  "pref_service_area": ["This field is required."],
  "employed": ["This field is required."],
  "shower": ["This field is required."],
  "hungry": ["This field is required."],
  "homeless": ["This field is required."]
}
```

### Scenario 2: Accessing Endpoint Without Authentication

**Request**:
```bash
curl -X GET http://localhost:8000/api/patients/
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Scenario 3: Accessing Endpoint with Wrong Role

**Request** (Form Manager trying to access Doctor endpoint):
```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer <form_manager_token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "call_next"}'
```

**Response** (403 Forbidden):
```json
{
  "detail": "Access Denied: You must have the 'doctor' role to access this resource."
}
```

---

## Error Response Structure

### Standard Error Format

Most errors follow this structure:

```json
{
  "field_name": ["Error message for this field."],
  "another_field": ["Another error message."]
}
```

Or for general errors:

```json
{
  "error": "Error message"
}
```

Or for authentication/permission errors:

```json
{
  "detail": "Error message",
  "code": "error_code"  // Optional
}
```

---

## Best Practices for Error Handling

### 1. Client-Side Validation

Validate data on the client side before sending to the API:

```javascript
function validatePatient(data) {
  const errors = {};
  
  if (!data.fname || data.fname.trim() === '') {
    errors.fname = 'Full name is required';
  }
  
  if (!data.phone || !/^\d{10}$/.test(data.phone)) {
    errors.phone = 'Phone must be 10 digits';
  }
  
  if (!data.ssn || !/^\d{10}$/.test(data.ssn)) {
    errors.ssn = 'SSN must be 10 digits';
  }
  
  // ... more validations
  
  return Object.keys(errors).length > 0 ? errors : null;
}
```

### 2. Handle Errors Gracefully

```javascript
async function createPatient(data) {
  try {
    const response = await fetch('http://localhost:8000/api/patients/', {
      method: 'POST',
      headers: {
        'Roni-Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      
      if (response.status === 400) {
        // Validation errors
        displayValidationErrors(errorData);
      } else if (response.status === 401) {
        // Authentication error
        redirectToLogin();
      } else if (response.status === 403) {
        // Permission error
        showPermissionError(errorData.detail);
      } else {
        // Other errors
        showGenericError('An error occurred. Please try again.');
      }
      
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error('Network error:', error);
    showNetworkError();
    return null;
  }
}
```

### 3. Implement Retry Logic

For transient errors (500, network errors), implement retry logic:

```javascript
async function apiCallWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 500 && i < maxRetries - 1) {
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => 
          setTimeout(resolve, Math.pow(2, i) * 1000)
        );
        continue;
      }
      
      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Wait before retrying
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

### 4. Display User-Friendly Messages

Map technical errors to user-friendly messages:

```javascript
const errorMessages = {
  'phone': {
    'Phone number must be a 10-digit number.': 
      'Please enter a valid 10-digit phone number (e.g., 5551234567)'
  },
  'ssn': {
    'SSN must be a 10-digit number.': 
      'Please enter a valid 10-digit SSN'
  },
  'image': {
    'Image size should not exceed 5 MB.': 
      'Please select a smaller image (maximum 5 MB)'
  }
};

function getUserFriendlyError(field, message) {
  return errorMessages[field]?.[message] || message;
}
```

### 5. Log Errors for Debugging

```javascript
function logError(context, error) {
  console.error(`[${new Date().toISOString()}] ${context}:`, error);
  
  // Send to error tracking service
  if (window.errorTrackingService) {
    window.errorTrackingService.captureException(error, {
      context: context,
      user: getCurrentUser()
    });
  }
}
```

---
*Last Updated: October 28, 2025*
