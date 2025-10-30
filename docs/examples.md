# API Usage Examples

## Complete Workflow Examples

### Example 1: Complete Patient Check-in Flow

This example demonstrates the entire process of logging in and checking in a patient.

#### Step 1: Login

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "12345678",
    "password": "formmanager123"
  }'
```

**Response**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "form"
}
```

#### Step 2: Check-in Patient

```bash
curl -X POST http://localhost:8000/api/patients/ \
  -H "Roni-Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
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
  -F "medicaid_no=9876543210" \
  -F "id_card=yes" \
  -F "insurance=humana" \
  -F "race=caucasian" \
  -F "pref_service_area=east_end" \
  -F "employed=yes" \
  -F "shower=no" \
  -F "hungry=yes" \
  -F "homeless=no" \
  -F "image=@patient_photo.jpg"
```

**Response** (201 Created):
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
  "medicaid_no": "9876543210",
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

**Side Effects**:
- Patient added to waiting queue
- WebSocket event sent to all connected clients
- Email notification sent to administrators

---

### Example 2: Doctor Workflow - Managing Consultations

#### Step 1: Login as Doctor

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "87654321",
    "password": "doctor123"
  }'
```

**Response**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "role": "doctor"
}
```

#### Step 2: View Queue

```bash
curl -X GET http://localhost:8000/api/queue/ \
  -H "Content-Type: application/json"
```

**Response** (200 OK):
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
    "status": "waiting",
    "check_in_time": "2025-10-28T10:35:00Z"
  }
]
```

#### Step 3: Call Next Patient

```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "action": "call_next"
  }'
```

**Response** (200 OK):
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

**Side Effects**:
- Patient status updated to "completed"
- `called_at` timestamp recorded
- WebSocket event sent to all connected clients

#### Step 4: Complete Consultation

```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Roni-Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "action": "complete",
    "patient_id": 1
  }'
```

**Response** (200 OK):
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

**Side Effects**:
- Patient status updated to "completed"
- `check_out_time` timestamp recorded
- Wait time calculated and stored
- WebSocket event sent to all connected clients

---

## JavaScript/React Examples

### Example 3: React Patient Registration Form

```javascript
import React, { useState } from 'react';

function PatientRegistrationForm() {
  const [formData, setFormData] = useState({
    fname: '',
    dob: '',
    gender: '',
    pronoun: '',
    phone: '',
    emergency_contact: '',
    ssn: '',
    street1: '',
    street2: '',
    last_known_address: '',
    city: '',
    state: '',
    zip: '',
    medicaid_no: '',
    id_card: '',
    insurance: '',
    race: '',
    pref_service_area: '',
    employed: '',
    shower: '',
    hungry: '',
    homeless: '',
    image: null
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    
    if (name === 'image') {
      setFormData(prev => ({ ...prev, image: files[0] }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors({});

    const accessToken = localStorage.getItem('access_token');
    
    // Create FormData for multipart/form-data
    const data = new FormData();
    Object.keys(formData).forEach(key => {
      if (formData[key] !== null && formData[key] !== '') {
        data.append(key, formData[key]);
      }
    });

    try {
      const response = await fetch('http://localhost:8000/api/patients/', {
        method: 'POST',
        headers: {
          'Roni-Authorization': `Bearer ${accessToken}`
        },
        body: data
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        if (response.status === 400) {
          setErrors(errorData);
        } else if (response.status === 401) {
          alert('Session expired. Please login again.');
          window.location.href = '/login';
        } else {
          alert('An error occurred. Please try again.');
        }
        
        setIsSubmitting(false);
        return;
      }

      const patient = await response.json();
      alert(`Patient ${patient.fname} checked in successfully!`);
      
      // Reset form
      setFormData({
        fname: '', dob: '', gender: '', pronoun: '', phone: '',
        emergency_contact: '', ssn: '', street1: '', street2: '',
        last_known_address: '', city: '', state: '', zip: '',
        medicaid_no: '', id_card: '', insurance: '', race: '',
        pref_service_area: '', employed: '', shower: '', hungry: '',
        homeless: '', image: null
      });
      
    } catch (error) {
      console.error('Network error:', error);
      alert('Network error. Please check your connection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="patient-form">
      <h2>Patient Check-In</h2>
      
      {/* Personal Information */}
      <section>
        <h3>Personal Information</h3>
        
        <div className="form-group">
          <label>Full Name *</label>
          <input
            type="text"
            name="fname"
            value={formData.fname}
            onChange={handleChange}
            required
          />
          {errors.fname && <span className="error">{errors.fname[0]}</span>}
        </div>

        <div className="form-group">
          <label>Date of Birth *</label>
          <input
            type="date"
            name="dob"
            value={formData.dob}
            onChange={handleChange}
            required
          />
          {errors.dob && <span className="error">{errors.dob[0]}</span>}
        </div>

        <div className="form-group">
          <label>Gender *</label>
          <select name="gender" value={formData.gender} onChange={handleChange} required>
            <option value="">Select...</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
          {errors.gender && <span className="error">{errors.gender[0]}</span>}
        </div>

        <div className="form-group">
          <label>Pronoun *</label>
          <select name="pronoun" value={formData.pronoun} onChange={handleChange} required>
            <option value="">Select...</option>
            <option value="he/him">He/Him</option>
            <option value="she/her">She/Her</option>
          </select>
          {errors.pronoun && <span className="error">{errors.pronoun[0]}</span>}
        </div>

        {/* Add more fields... */}
      </section>

      {/* Image Upload */}
      <section>
        <div className="form-group">
          <label>Photo</label>
          <input
            type="file"
            name="image"
            accept="image/jpeg,image/png"
            onChange={handleChange}
          />
          {errors.image && <span className="error">{errors.image[0]}</span>}
        </div>
      </section>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Checking In...' : 'Check In Patient'}
      </button>
    </form>
  );
}

export default PatientRegistrationForm;
```

---

### Example 4: Login Component

```javascript
import React, { useState } from 'react';

function LoginForm() {
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token, password })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Login failed');
        setIsLoading(false);
        return;
      }

      // Store tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user_role', data.role);

      // Redirect based on role
      switch(data.role) {
        case 'form':
          window.location.href = '/patient-registration';
          break;
        case 'doctor':
          window.location.href = '/doctor-dashboard';
          break;
        case 'queue':
          window.location.href = '/queue-monitor';
          break;
        default:
          window.location.href = '/';
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin} className="login-form">
      <h2>Login</h2>
      
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label>Token</label>
        <input
          type="text"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Enter 8-digit token"
          maxLength={8}
          required
        />
      </div>

      <div className="form-group">
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
          required
        />
      </div>

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

export default LoginForm;
```

---

### Example 5: Doctor Dashboard with Queue Management

```javascript
import React, { useState, useEffect } from 'react';

function DoctorDashboard() {
  const [queue, setQueue] = useState([]);
  const [currentPatient, setCurrentPatient] = useState(null);
  const [socket, setSocket] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Fetch initial queue
    fetchQueue();

    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/queue/');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleQueueUpdate(data);
    };

    setSocket(ws);

    return () => ws.close();
  }, []);

  const fetchQueue = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/queue/');
      const data = await response.json();
      setQueue(data);
      
      const inConsultation = data.find(entry => entry.status === 'completed');
      setCurrentPatient(inConsultation);
    } catch (error) {
      console.error('Error fetching queue:', error);
    }
  };

  const handleQueueUpdate = (data) => {
    switch(data.event) {
      case 'PATIENT_ADDED':
        fetchQueue(); // Refresh queue
        break;
      case 'PATIENT_COMPLETED':
        setCurrentPatient(data.patient);
        break;
      case 'PATIENT_COMPLETED':
        setCurrentPatient(null);
        fetchQueue(); // Refresh queue
        break;
    }
  };

  const callNextPatient = async () => {
    setIsLoading(true);
    const accessToken = localStorage.getItem('access_token');

    try {
      const response = await fetch('http://localhost:8000/api/doctors/', {
        method: 'POST',
        headers: {
          'Roni-Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'call_next' })
      });

      if (!response.ok) {
        const data = await response.json();
        alert(data.error || 'Failed to call next patient');
        return;
      }

      const data = await response.json();
      setCurrentPatient(data.patient);
    } catch (error) {
      console.error('Error calling next patient:', error);
      alert('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const completeConsultation = async () => {
    if (!currentPatient) return;

    setIsLoading(true);
    const accessToken = localStorage.getItem('access_token');

    try {
      const response = await fetch('http://localhost:8000/api/doctors/', {
        method: 'POST',
        headers: {
          'Roni-Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: 'complete',
          patient_id: currentPatient.id
        })
      });

      if (!response.ok) {
        const data = await response.json();
        alert(data.error || 'Failed to complete consultation');
        return;
      }

      setCurrentPatient(null);
      alert('Consultation completed successfully');
    } catch (error) {
      console.error('Error completing consultation:', error);
      alert('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const waitingPatients = queue.filter(entry => entry.status === 'waiting');

  return (
    <div className="doctor-dashboard">
      <h2>Doctor Dashboard</h2>

      {/* Current Patient */}
      <section className="current-patient">
        <h3>Current Patient</h3>
        {currentPatient ? (
          <div className="patient-card active">
            {currentPatient.image && (
              <img src={currentPatient.image} alt={currentPatient.fname} />
            )}
            <h4>{currentPatient.fname}</h4>
            <button 
              onClick={completeConsultation}
              disabled={isLoading}
            >
              Complete Consultation
            </button>
          </div>
        ) : (
          <p>No patient in consultation</p>
        )}
      </section>

      {/* Waiting Queue */}
      <section className="waiting-queue">
        <h3>Waiting Queue ({waitingPatients.length})</h3>
        
        {waitingPatients.length > 0 ? (
          <>
            <button 
              onClick={callNextPatient}
              disabled={isLoading || currentPatient !== null}
            >
              Call Next Patient
            </button>
            
            <div className="queue-list">
              {waitingPatients.map((entry, index) => (
                <div key={entry.id} className="queue-item">
                  <span className="position">{index + 1}</span>
                  {entry.patient.image && (
                    <img src={entry.patient.image} alt={entry.patient.fname} />
                  )}
                  <span className="name">{entry.patient.fname}</span>
                  <span className="time">
                    Waiting since {new Date(entry.check_in_time).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p>No patients waiting</p>
        )}
      </section>
    </div>
  );
}

export default DoctorDashboard;
```

---

## Python Examples

### Example 6: Python Script for Patient Check-in

```python
import requests
import json

BASE_URL = 'http://localhost:8000/api'

def login(token, password):
    """Login and return access token"""
    url = f'{BASE_URL}/login/'
    data = {
        'token': token,
        'password': password
    }
    
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    return result['access'], result['role']

def checkin_patient(access_token, patient_data, image_path=None):
    """Check in a new patient"""
    url = f'{BASE_URL}/patients/'
    headers = {
        'Roni-Authorization': f'Bearer {access_token}'
    }
    
    files = {}
    if image_path:
        files['image'] = open(image_path, 'rb')
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=patient_data,
            files=files
        )
        response.raise_for_status()
        return response.json()
    finally:
        if image_path:
            files['image'].close()

# Usage
if __name__ == '__main__':
    # Login
    access_token, role = login('12345678', 'formmanager123')
    print(f'Logged in with role: {role}')
    
    # Patient data
    patient_data = {
        'fname': 'John Doe',
        'dob': '1990-05-15',
        'gender': 'male',
        'pronoun': 'he/him',
        'phone': '5551234567',
        'emergency_contact': 'Jane Doe - 5559876543',
        'ssn': '1234567890',
        'street1': '123 Main Street',
        'street2': 'Apt 4B',
        'last_known_address': '123 Main Street, Apt 4B',
        'city': 'Richmond',
        'state': 'VA',
        'zip': '23219',
        'medicaid_no': '9876543210',
        'id_card': 'yes',
        'insurance': 'humana',
        'race': 'caucasian',
        'pref_service_area': 'east_end',
        'employed': 'yes',
        'shower': 'no',
        'hungry': 'yes',
        'homeless': 'no'
    }
    
    # Check in patient
    patient = checkin_patient(
        access_token,
        patient_data,
        image_path='patient_photo.jpg'
    )
    
    print(f"Patient checked in: {patient['fname']} (ID: {patient['id']})")
```

---

### Example 7: Python Doctor Script

```python
import requests

BASE_URL = 'http://localhost:8000/api'

class DoctorAPI:
    def __init__(self, token, password):
        self.access_token = self._login(token, password)
        self.headers = {
            'Roni-Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def _login(self, token, password):
        """Login and return access token"""
        url = f'{BASE_URL}/login/'
        response = requests.post(url, json={
            'token': token,
            'password': password
        })
        response.raise_for_status()
        return response.json()['access']
    
    def get_queue(self):
        """Get current queue"""
        url = f'{BASE_URL}/queue/'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def call_next_patient(self):
        """Call next patient to consultation"""
        url = f'{BASE_URL}/doctors/'
        response = requests.post(
            url,
            headers=self.headers,
            json={'action': 'call_next'}
        )
        response.raise_for_status()
        return response.json()
    
    def complete_consultation(self, patient_id):
        """Complete patient consultation"""
        url = f'{BASE_URL}/doctors/'
        response = requests.post(
            url,
            headers=self.headers,
            json={
                'action': 'complete',
                'patient_id': patient_id
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
if __name__ == '__main__':
    doctor = DoctorAPI('87654321', 'doctor123')
    
    # View queue
    queue = doctor.get_queue()
    print(f"Patients in queue: {len(queue)}")
    for entry in queue:
        print(f"  - {entry['patient']['fname']} ({entry['status']})")
    
    # Call next patient
    if any(e['status'] == 'waiting' for e in queue):
        result = doctor.call_next_patient()
        patient = result['patient']
        print(f"\nCalled patient: {patient['fname']}")
        
        # Simulate consultation
        input("Press Enter when consultation is complete...")
        
        # Complete consultation
        result = doctor.complete_consultation(patient['id'])
        print(f"Completed consultation for: {result['patient']['fname']}")
```

---

## Postman Collection

You can import this JSON into Postman to test all endpoints:

```json
{
  "info": {
    "name": "CheckIn API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api"
    },
    {
      "key": "access_token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"token\": \"12345678\",\n  \"password\": \"your-password\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/login/",
          "host": ["{{base_url}}"],
          "path": ["login", ""]
        }
      }
    },
    {
      "name": "Create Patient",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Roni-Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "body": {
          "mode": "formdata",
          "formdata": [
            {"key": "fname", "value": "John Doe", "type": "text"},
            {"key": "dob", "value": "1990-05-15", "type": "text"},
            {"key": "gender", "value": "male", "type": "text"}
          ]
        },
        "url": {
          "raw": "{{base_url}}/patients/",
          "host": ["{{base_url}}"],
          "path": ["patients", ""]
        }
      }
    }
  ]
}
```

---
*Last Updated: October 28, 2025*
