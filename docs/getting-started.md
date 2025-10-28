# Getting Started

## Prerequisites

- Python 3.12+
- Redis Server
- Virtual Environment (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CheckIn
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Linux/Mac
# or
env\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost

# Site URLs
SITE_URL=http://localhost:9000
SITE_DOMAIN=http://localhost:8000

# Database (SQLite default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media

# Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=UTC

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=webmaster@localhost

# Security
CSRF_TRUSTED_ORIGINS=
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Create Access Tokens

Access the Django admin panel at `http://localhost:8000/admin/` and create Access Tokens for different roles:

1. Navigate to **Access Tokens**
2. Click **Add Access Token**
3. Fill in:
   - **Password**: Choose a secure password
   - **Role**: Select from `form`, `doctor`, or `queue`
   - **Is Active**: Check this box

The system will auto-generate an 8-digit token.

### 8. Start Redis Server

```bash
redis-server
```

### 9. Start Celery Worker

In a new terminal:

```bash
celery -A CheckIn worker -l info
```

### 10. Start Celery Beat (Optional - for scheduled tasks)

In another terminal:

```bash
celery -A CheckIn beat -l info
```

### 11. Start Development Server

```bash
daphne -b 0.0.0.0 -p 8000 CheckIn.asgi:application
```

The API will be available at `http://localhost:8000/api/`

**Note**: This is an ASGI application using Daphne server to support WebSocket connections.

## Testing the API

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "12345678",
    "password": "your-password"
  }'
```

### Using Postman

1. Import the API endpoints from this documentation
2. Set up environment variables for base URL and tokens
3. Start testing endpoints

## Next Steps

- Read the [Authentication](authentication.md) guide
- Explore [API Endpoints](api-endpoints.md)
- Learn about [WebSocket Events](websocket.md)

---

**Developer**: Roni Ahamed - Backend Developer

*Last Updated: October 28, 2025*
