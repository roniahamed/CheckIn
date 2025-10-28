# CheckIn - Patient Management System

A comprehensive Django-based patient management and queue system for healthcare facilities with real-time updates and role-based access control.

## 🚀 Features

- **Role-Based Authentication**: JWT-based authentication with three distinct roles (Form Manager, Doctor, Queue Manager)
- **Patient Management**: Complete patient registration with comprehensive data collection
- **Real-Time Queue**: Live queue updates via WebSocket for seamless patient flow
- **Email Notifications**: Automated email alerts on patient check-in
- **Image Upload**: Patient photo capture and storage
- **RESTful API**: Well-documented API endpoints for easy integration

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Getting Started](docs/getting-started.md)** - Installation and setup guide
- **[Authentication](docs/authentication.md)** - Authentication flow and JWT usage
- **[API Endpoints](docs/api-endpoints.md)** - Complete API reference with request/response examples
- **[WebSocket Events](docs/websocket.md)** - Real-time event documentation
- **[Data Models](docs/data-models.md)** - Database schema and model details
- **[Error Handling](docs/error-handling.md)** - Error codes and troubleshooting
- **[Examples](docs/examples.md)** - Code examples in JavaScript, Python, React
- **[Quick Reference](docs/quick-reference.md)** - Cheat sheet for common tasks
- **[Production Deployment](docs/deployment.md)** - Nginx, Gunicorn, systemd setup

## 🛠️ Tech Stack

- **Backend**: Django 5.2+ with Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Real-time**: Django Channels + Redis
- **Task Queue**: Celery
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Admin**: Django Unfold

## 🚦 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Services

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery
celery -A CheckIn worker -l info

# Terminal 3: ASGI Server (Daphne)
daphne -b 0.0.0.0 -p 8000 CheckIn.asgi:application
```

### 5. Access the System

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **WebSocket**: ws://localhost:8000/ws/queue/

## 📋 API Overview

### Authentication

```bash
# Login
POST /api/login/
{
  "token": "12345678",
  "password": "your-password"
}
```

### Patient Management (Form Manager)

```bash
# Register patient
POST /api/patients/
# Requires: Form Manager role
# Accepts: multipart/form-data with patient details + optional image
```

### Doctor Management

```bash
# Call next patient
POST /api/doctors/
{
  "action": "call_next"
}

# Complete consultation
POST /api/doctors/
{
  "action": "complete",
  "patient_id": 1
}
```

### Queue Status

```bash
# Get current queue
GET /api/queue/
```

## 🔐 Access Roles

| Role | Access Token Value | Permissions |
|------|-------------------|-------------|
| Form Manager | `form` | Register patients |
| Doctor | `doctor` | Manage consultations |
| Queue Manager | `queue` | View queue |

Create access tokens in the Django admin panel at `/admin/`.

## 📡 WebSocket Events

Connect to `ws://localhost:8000/ws/queue/` to receive real-time updates:

- **PATIENT_ADDED** - New patient checked in
- **PATIENT_CALLED** - Patient called to consultation  
- **PATIENT_COMPLETED** - Consultation finished

## 🔧 Development

### Project Structure

```
CheckIn/
├── CheckIn/          # Project settings
├── management/       # Main app (models, views, serializers)
├── docs/            # Documentation
├── media/           # Uploaded files
├── templates/       # Email templates
└── requirements.txt # Dependencies
```

### Running Tests

```bash
python manage.py test
```

## 📝 Environment Variables

See [Getting Started](docs/getting-started.md) for a complete list of environment variables.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This is a client project. All rights reserved by the client.

## �‍💻 Developer

**Roni Ahamed**  
Backend Developer

## �📞 Support

For detailed API documentation and examples, please refer to the [documentation](docs/) folder.

---

**Last Updated**: October 28, 2025
