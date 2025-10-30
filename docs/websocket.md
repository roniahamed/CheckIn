# WebSocket Events

## Overview

The CheckIn system uses WebSockets for real-time queue updates. When patients are added, called, or completed, all connected clients receive instant notifications.

## WebSocket Connection

### Connection URL

```
ws://localhost:8000/ws/queue/
```

For production (with HTTPS):
```
wss://your-domain.com/ws/queue/
```

### Connecting to WebSocket

**JavaScript Example**:
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/queue/');

socket.onopen = function(e) {
  console.log('WebSocket connection established');
};

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received event:', data);
  handleQueueUpdate(data);
};

socket.onerror = function(error) {
  console.error('WebSocket error:', error);
};

socket.onclose = function(event) {
  console.log('WebSocket connection closed:', event.code, event.reason);
};
```

**Python Example** (using websockets library):
```python
import asyncio
import websockets
import json

async def listen_to_queue():
    uri = "ws://localhost:8000/ws/queue/"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        async for message in websocket:
            data = json.loads(message)
            print(f"Received event: {data}")
            handle_queue_update(data)

asyncio.run(listen_to_queue())
```

## Event Types

The WebSocket sends two types of events:

| Event Type | Trigger | Description |
|------------|---------|-------------|
| `PATIENT_ADDED` | Patient check-in | New patient added to queue |
| `PATIENT_COMPLETED` | Doctor calls next | Patient immediately completed (no consultation state) |

## Event Structures

### 1. PATIENT_ADDED

**Triggered by**: `POST /api/patients/` (Patient check-in)

**Event Structure**:
```json
{
  "type": "send.queue.update",
  "event": "PATIENT_ADDED",
  "patient": {
    "id": 1,
    "fname": "John Doe",
    "status": "waiting",
    "image": "/media/patient_images/john_doe_abc123.jpg"
  }
}
```

**Field Descriptions**:
- `type` (string): Internal message type (always "send.queue.update")
- `event` (string): Event identifier ("PATIENT_ADDED")
- `patient` (object): Patient information
  - `id` (integer): Patient database ID
  - `fname` (string): Patient full name
  - `status` (string): Current status (always "waiting" for this event)
  - `image` (string|null): Patient photo URL or null if no image

**Example Handler**:
```javascript
function handlePatientAdded(data) {
  const patient = data.patient;
  
  // Add patient to queue UI
  const queueItem = createQueueItem(patient);
  document.getElementById('waiting-queue').appendChild(queueItem);
  
  // Show notification
  showNotification(`New patient: ${patient.fname}`);
  
  // Update queue count
  updateQueueCount();
}
```



### 3. PATIENT_COMPLETED

**Triggered by**: `POST /api/doctors/` with action "complete"

**Event Structure**:
```json
{
  "type": "send.queue.update",
  "event": "PATIENT_COMPLETED",
  "patient": {
    "id": 1,
    "fname": "John Doe",
    "status": "completed",
    "image": "/media/patient_images/john_doe_abc123.jpg"
  }
}
```

**Field Descriptions**:
- `type` (string): Internal message type (always "send.queue.update")
- `event` (string): Event identifier ("PATIENT_COMPLETED")
- `patient` (object): Patient information
  - `id` (integer): Patient database ID
  - `fname` (string): Patient full name
  - `status` (string): Current status (always "completed" for this event)
  - `image` (string|null): Patient photo URL or null if no image

**Example Handler**:
```javascript
function handlePatientCompleted(data) {
  const patient = data.patient;
  
  // Remove patient from active queue
  const patientElement = document.getElementById(`patient-${patient.id}`);
  patientElement.classList.add('fade-out');
  
  setTimeout(() => {
    patientElement.remove();
  }, 500);
  
  // Show notification
  showNotification(`${patient.fname} consultation completed`);
  
  // Update queue count
  updateQueueCount();
}
```

## Complete Integration Example

### React Example

```javascript
import React, { useEffect, useState } from 'react';

function QueueMonitor() {
  const [queue, setQueue] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/queue/');
    
    ws.onopen = () => {
      console.log('Connected to queue updates');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleQueueUpdate(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('Disconnected from queue updates');
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    setSocket(ws);

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, []);

  const handleQueueUpdate = (data) => {
    switch(data.event) {
      case 'PATIENT_ADDED':
        setQueue(prev => [...prev, data.patient]);
        break;
      

      
      case 'PATIENT_COMPLETED':
        setQueue(prev => 
          prev.filter(p => p.id !== data.patient.id)
        );
        break;
      
      default:
        console.log('Unknown event:', data.event);
    }
  };

  return (
    <div className="queue-monitor">
      <h2>Patient Queue</h2>
      <div className="waiting-section">
        <h3>Waiting ({queue.filter(p => p.status === 'waiting').length})</h3>
        {queue
          .filter(p => p.status === 'waiting')
          .map(patient => (
            <div key={patient.id} className="patient-card">
              {patient.image && <img src={patient.image} alt={patient.fname} />}
              <span>{patient.fname}</span>
            </div>
          ))}
      </div>
      

    </div>
  );
}

export default QueueMonitor;
```

### Vanilla JavaScript Example

```javascript
class QueueManager {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.socket = null;
    this.queue = [];
    this.connect();
  }

  connect() {
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.onConnectionChange(true);
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.onConnectionChange(false);
      // Reconnect after 3 seconds
      setTimeout(() => this.connect(), 3000);
    };
  }

  handleEvent(data) {
    switch(data.event) {
      case 'PATIENT_ADDED':
        this.addPatient(data.patient);
        break;

      case 'PATIENT_COMPLETED':
        this.removePatient(data.patient.id);
        break;
    }
  }

  addPatient(patient) {
    this.queue.push(patient);
    this.renderQueue();
  }

  updatePatientStatus(patientId, status) {
    const patient = this.queue.find(p => p.id === patientId);
    if (patient) {
      patient.status = status;
      this.renderQueue();
    }
  }

  removePatient(patientId) {
    this.queue = this.queue.filter(p => p.id !== patientId);
    this.renderQueue();
  }

  renderQueue() {
    // Implement your UI rendering logic here
    console.log('Current queue:', this.queue);
  }

  onConnectionChange(isConnected) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
      indicator.className = isConnected ? 'connected' : 'disconnected';
      indicator.textContent = isConnected ? 'Connected' : 'Disconnected';
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

// Usage
const queueManager = new QueueManager('ws://localhost:8000/ws/queue/');
```

## Connection Management

### Reconnection Strategy

Implement automatic reconnection when the WebSocket connection drops:

```javascript
class ReconnectingWebSocket {
  constructor(url, options = {}) {
    this.url = url;
    this.reconnectInterval = options.reconnectInterval || 3000;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    this.reconnectAttempts = 0;
    this.shouldReconnect = true;
    
    this.connect();
  }

  connect() {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log('Connected');
      this.reconnectAttempts = 0;
      if (this.onopen) this.onopen();
    };

    this.socket.onmessage = (event) => {
      if (this.onmessage) this.onmessage(event);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (this.onerror) this.onerror(error);
    };

    this.socket.onclose = () => {
      console.log('Connection closed');
      if (this.onclose) this.onclose();
      
      if (this.shouldReconnect && 
          this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        setTimeout(() => this.connect(), this.reconnectInterval);
      }
    };
  }

  send(data) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(data);
    } else {
      console.error('WebSocket is not open. Current state:', this.socket.readyState);
    }
  }

  close() {
    this.shouldReconnect = false;
    this.socket.close();
  }
}

// Usage
const ws = new ReconnectingWebSocket('ws://localhost:8000/ws/queue/', {
  reconnectInterval: 3000,
  maxReconnectAttempts: 10
});

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Error Handling

### Connection Errors

```javascript
socket.onerror = function(error) {
  console.error('WebSocket error:', error);
  
  // Show user notification
  showErrorNotification('Connection error. Retrying...');
  
  // Log to error tracking service
  logError('WebSocket Error', error);
};
```

### Message Parsing Errors

```javascript
socket.onmessage = function(event) {
  try {
    const data = JSON.parse(event.data);
    handleQueueUpdate(data);
  } catch (error) {
    console.error('Failed to parse WebSocket message:', error);
    console.error('Raw message:', event.data);
  }
};
```

## Testing WebSocket Events

### Using wscat

Install wscat:
```bash
npm install -g wscat
```

Connect to WebSocket:
```bash
wscat -c ws://localhost:8000/ws/queue/
```

You'll receive events in real-time as they occur.

### Using Python

```python
import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws/queue/"
    async with websockets.connect(uri) as websocket:
        print("Connected. Listening for events...")
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(test_websocket())
```

## Best Practices

1. **Always handle reconnection**: Networks are unreliable; implement automatic reconnection
2. **Parse messages safely**: Use try-catch when parsing JSON
3. **Validate event types**: Check event type before processing
4. **Update UI efficiently**: Batch updates when possible
5. **Show connection status**: Let users know if they're connected
6. **Handle errors gracefully**: Don't let WebSocket errors crash your app
7. **Clean up on unmount**: Close WebSocket connections when components unmount

---
*Last Updated: October 28, 2025*
