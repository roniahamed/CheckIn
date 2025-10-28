# CheckIn API Documentation

## Overview

CheckIn is a Django-based patient management system designed for healthcare facilities. The system allows staff to check-in patients, manage queues, and facilitate doctor-patient consultations through a REST API with real-time WebSocket updates.

## Table of Contents

1. [Getting Started](getting-started.md)
2. [Authentication](authentication.md)
3. [API Endpoints](api-endpoints.md)
4. [API Specification](api-specification.md)
5. [WebSocket Events](websocket.md)
6. [Data Models](data-models.md)
7. [Error Handling](error-handling.md)
8. [Examples](examples.md)
9. [Quick Reference](quick-reference.md)
10. [Production Deployment](deployment.md)

## Key Features

- **Role-Based Access Control**: Three distinct roles (Form Manager, Doctor, Queue Manager)
- **Patient Management**: Comprehensive patient registration and tracking
- **Queue Management**: Real-time queue system for patient flow
- **WebSocket Support**: Live updates for queue changes
- **Email Notifications**: Automated email notifications on patient check-in
- **Image Upload**: Support for patient photo uploads

## System Architecture

- **Backend**: Django 5.2+ with Django REST Framework
- **Authentication**: JWT (JSON Web Token) based authentication
- **Real-time Updates**: Django Channels with Redis
- **Task Queue**: Celery for asynchronous tasks
- **Database**: SQLite (development) / PostgreSQL (production recommended)

## Base URL

```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Quick Links

- **API Base URL**: `/api/`
- **Admin Panel**: `/admin/`
- **WebSocket URL**: `ws://localhost:8000/ws/queue/`

## License

This is a client project. All rights reserved by the client.

## Developer

**Roni Ahamed**  
Backend Developer

## Support

For issues or questions, please contact the development team or refer to the detailed documentation sections.

---
*Last Updated: October 28, 2025*
