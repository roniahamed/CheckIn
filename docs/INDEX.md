# Documentation Index

Welcome to the CheckIn API Documentation! This index provides an overview of all available documentation.

---

## 📖 Documentation Files

### 🚀 Getting Started
**[getting-started.md](getting-started.md)** (2.8 KB)
- Prerequisites and installation
- Environment setup
- Database migrations
- Running the development server
- Creating access tokens

**Start here if**: You're setting up the project for the first time.

---

### 🔐 Authentication
**[authentication.md](authentication.md)** (5.4 KB)
- JWT authentication flow
- Role-based access control (Form, Doctor, Queue)
- Login process
- Token refresh
- Security best practices

**Start here if**: You need to understand how to authenticate with the API.

---

### 📡 API Reference
**[api-endpoints.md](api-endpoints.md)** (12 KB)
- Complete endpoint documentation
- Request/response examples
- Field descriptions
- cURL examples
- HTTP status codes

**Start here if**: You need detailed information about specific endpoints.

**[api-specification.md](api-specification.md)** (11 KB)
- Formal API specification v1.0
- Data type definitions
- Complete error reference
- Field enumerations
- Protocol specifications

**Start here if**: You need a technical specification document.

---

### 🔌 Real-Time Features
**[websocket.md](websocket.md)** (14 KB)
- WebSocket connection guide
- Event types and structures
- JavaScript/React examples
- Python examples
- Reconnection strategies

**Start here if**: You need to implement real-time queue updates.

---

### 🗄️ Data & Models
**[data-models.md](data-models.md)** (11 KB)
- Database schema
- Model relationships
- Field specifications
- Common queries
- Visual diagrams

**Start here if**: You need to understand the database structure.

---

### ❌ Error Handling
**[error-handling.md](error-handling.md)** (12 KB)
- HTTP status codes
- Error response formats
- Validation errors
- Troubleshooting guide
- Best practices

**Start here if**: You're debugging errors or implementing error handling.

---

### 💡 Code Examples
**[examples.md](examples.md)** (24 KB)
- Complete workflow examples
- React components
- Python scripts
- JavaScript integration
- Postman collection

**Start here if**: You want to see working code examples.

---

### ⚡ Quick Reference
**[quick-reference.md](quick-reference.md)** (6.5 KB)
- Quick command reference
- Common tasks
- Field constraints
- Troubleshooting tips
- Data flow diagram

**Start here if**: You need a quick cheat sheet.

---

## 📋 By Use Case

### I want to...

#### Set up the project
1. [Getting Started](getting-started.md)
2. [Authentication](authentication.md)

#### Build a frontend application
1. [Authentication](authentication.md)
2. [API Endpoints](api-endpoints.md)
3. [WebSocket Events](websocket.md)
4. [Examples](examples.md) - React components

#### Understand the API
1. [API Specification](api-specification.md)
2. [Data Models](data-models.md)
3. [Quick Reference](quick-reference.md)

#### Integrate with Python
1. [Authentication](authentication.md)
2. [API Endpoints](api-endpoints.md)
3. [Examples](examples.md) - Python scripts

#### Debug issues
1. [Error Handling](error-handling.md)
2. [Quick Reference](quick-reference.md) - Troubleshooting section

#### Implement real-time updates
1. [WebSocket Events](websocket.md)
2. [Examples](examples.md) - WebSocket examples

---

## 📊 Documentation Statistics

- **Total Files**: 11 markdown files
- **Total Size**: ~112 KB
- **Code Examples**: 50+ examples
- **Languages Covered**: JavaScript, Python, React, cURL, Bash
- **Endpoints Documented**: 6 endpoints (100% coverage)
- **WebSocket Events**: 3 event types

---

## 🎯 Quick Links by Role

### Form Manager (Patient Registration)
- [Getting Started](getting-started.md)
- [Authentication](authentication.md) - Form Manager role
- [API Endpoints](api-endpoints.md#21-create-patient-check-in) - POST /api/patients/
- [Examples](examples.md#example-3-react-patient-registration-form)

### Doctor (Managing Consultations)
- [Authentication](authentication.md) - Doctor role
- [API Endpoints](api-endpoints.md#3-doctor-management)
- [WebSocket Events](websocket.md) - Real-time updates
- [Examples](examples.md#example-5-doctor-dashboard-with-queue-management)

### Developer (Integration)
- [API Specification](api-specification.md)
- [Data Models](data-models.md)
- [Error Handling](error-handling.md)
- [Examples](examples.md)

---

## 🔍 Search by Topic

### Authentication & Security
- [Authentication](authentication.md)
- [Error Handling](error-handling.md#authentication-errors)
- [Quick Reference](quick-reference.md#authentication-header)

### Patient Management
- [API Endpoints](api-endpoints.md#2-patient-management)
- [Data Models](data-models.md#patient-model)
- [Examples](examples.md#example-1-complete-patient-check-in-flow)

### Queue System
- [API Endpoints](api-endpoints.md#4-queue-management)
- [WebSocket Events](websocket.md)
- [Data Models](data-models.md#queueentry-model)

### Real-Time Updates
- [WebSocket Events](websocket.md)
- [Examples](examples.md#example-5-doctor-dashboard-with-queue-management)

### Errors & Debugging
- [Error Handling](error-handling.md)
- [Quick Reference](quick-reference.md#troubleshooting)

---

## 📱 Format Guide

### Markdown Features Used
- ✅ Headers and subheaders
- ✅ Code blocks with syntax highlighting
- ✅ Tables for structured data
- ✅ Links and cross-references
- ✅ Lists (ordered and unordered)
- ✅ Blockquotes for important notes
- ✅ Inline code formatting

### Code Block Languages
- `bash` - Shell commands
- `json` - JSON data
- `javascript` - JavaScript code
- `python` - Python code
- `http` - HTTP headers
- `jsx` - React components

---

## 🔄 Keeping Documentation Updated

This documentation is maintained alongside the codebase. When API changes occur:

1. Update the relevant documentation file(s)
2. Update the [CHANGELOG.md](CHANGELOG.md)
3. Update version numbers if needed
4. Cross-check examples still work

---

## 📞 Need Help?

Can't find what you're looking for?

1. Check the [Quick Reference](quick-reference.md) for common tasks
2. Search for keywords in [API Endpoints](api-endpoints.md)
3. Look at [Examples](examples.md) for working code
4. Review [Error Handling](error-handling.md) if encountering issues

---

## 📝 Additional Resources

- **[README.md](README.md)** - Documentation overview
- **[CHANGELOG.md](CHANGELOG.md)** - Documentation version history

---

*Last Updated: October 28, 2025*
