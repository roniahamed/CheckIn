# Quick Deployment Summary

## Complete Stack with Nginx, Gunicorn, Uvicorn, Celery, and Redis

This is a summary of the full production deployment setup. For detailed instructions, see [deployment.md](deployment.md).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                         Nginx                            │
│                  (Reverse Proxy + SSL)                   │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    ┌─────▼─────┐        ┌─────▼─────┐
    │   HTTP    │        │ WebSocket │
    │  Requests │        │  /ws/     │
    └─────┬─────┘        └─────┬─────┘
          │                     │
          └──────────┬──────────┘
                     │
         ┌───────────▼──────────┐
         │      Gunicorn         │
         │  (Uvicorn Workers)    │
         │   Django ASGI App     │
         └───────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌────▼────┐
   │ Celery  │      │  Redis  │
   │ Worker  │◄─────┤  Broker │
   └────┬────┘      └─────────┘
        │
   ┌────▼────┐
   │ Celery  │
   │  Beat   │
   └─────────┘
```

---

## Services Included

### 1. **Nginx** (Port 80/443)
- Reverse proxy
- Static file serving
- WebSocket proxying
- SSL/TLS termination
- **Auto-starts on boot**: ✅

### 2. **Gunicorn with Uvicorn Workers**
- ASGI application server
- Handles HTTP and WebSocket connections
- 4 worker processes (configurable)
- Unix socket communication with Nginx
- **Auto-starts on boot**: ✅
- **Auto-restarts on failure**: ✅

### 3. **Redis Server** (Port 6379)
- Message broker for Celery
- Channel layer for Django Channels (WebSocket)
- Result backend for Celery tasks
- **Auto-starts on boot**: ✅

### 4. **Celery Worker**
- Background task processing
- Email notifications
- Asynchronous operations
- 4 concurrent workers (configurable)
- **Auto-starts on boot**: ✅
- **Auto-restarts on failure**: ✅

### 5. **Celery Beat**
- Scheduled task execution
- Periodic tasks
- Database-backed scheduler
- **Auto-starts on boot**: ✅
- **Auto-restarts on failure**: ✅

---

## Quick Setup Commands

### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx redis-server
```

### 2. Install Python Dependencies
```bash
source env/bin/activate
pip install gunicorn uvicorn[standard]
```

### 3. Create Systemd Services

Create these three service files:

**a) Gunicorn Service**: `/etc/systemd/system/checkin-gunicorn.service`
```ini
[Unit]
Description=CheckIn Gunicorn Service
After=network.target redis.service

[Service]
Type=notify
User=roni
Group=roni
WorkingDirectory=/home/roni/Desktop/JVAI Projects/October/CheckIn
Environment="PATH=/home/roni/Desktop/JVAI Projects/October/CheckIn/env/bin"
ExecStart=/home/roni/Desktop/JVAI Projects/October/CheckIn/env/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind unix:/home/roni/Desktop/JVAI Projects/October/CheckIn/checkin.sock \
    --timeout 120 \
    --access-logfile /var/log/checkin/gunicorn-access.log \
    --error-logfile /var/log/checkin/gunicorn-error.log \
    CheckIn.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**b) Celery Worker Service**: `/etc/systemd/system/checkin-celery.service`
```ini
[Unit]
Description=CheckIn Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=roni
Group=roni
WorkingDirectory=/home/roni/Desktop/JVAI Projects/October/CheckIn
Environment="PATH=/home/roni/Desktop/JVAI Projects/October/CheckIn/env/bin"
ExecStart=/home/roni/Desktop/JVAI Projects/October/CheckIn/env/bin/celery -A CheckIn worker \
    --loglevel=info \
    --logfile=/var/log/checkin/celery-worker.log \
    --pidfile=/var/run/celery/worker.pid \
    --concurrency=4
Restart=always

[Install]
WantedBy=multi-user.target
```

**c) Celery Beat Service**: `/etc/systemd/system/checkin-celery-beat.service`
```ini
[Unit]
Description=CheckIn Celery Beat
After=network.target redis.service checkin-celery.service

[Service]
Type=simple
User=roni
Group=roni
WorkingDirectory=/home/roni/Desktop/JVAI Projects/October/CheckIn
Environment="PATH=/home/roni/Desktop/JVAI Projects/October/CheckIn/env/bin"
ExecStart=/home/roni/Desktop/JVAI Projects/October/CheckIn/env/bin/celery -A CheckIn beat \
    --loglevel=info \
    --logfile=/var/log/checkin/celery-beat.log \
    --pidfile=/var/run/celery/beat.pid \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Create Log Directories
```bash
sudo mkdir -p /var/log/checkin
sudo chown roni:roni /var/log/checkin

sudo mkdir -p /var/run/celery
sudo chown roni:roni /var/run/celery
```

### 5. Configure Nginx

Create `/etc/nginx/sites-available/checkin`:
```nginx
upstream checkin_app {
    server unix:/home/roni/Desktop/JVAI\ Projects/October/CheckIn/checkin.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /home/roni/Desktop/JVAI\ Projects/October/CheckIn/staticfiles/;
    }

    location /media/ {
        alias /home/roni/Desktop/JVAI\ Projects/October/CheckIn/media/;
    }

    location / {
        proxy_pass http://checkin_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /ws/ {
        proxy_pass http://checkin_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/checkin /etc/nginx/sites-enabled/
sudo nginx -t
```

### 6. Enable All Services (Auto-start on Boot)
```bash
sudo systemctl daemon-reload
sudo systemctl enable redis-server
sudo systemctl enable checkin-gunicorn
sudo systemctl enable checkin-celery
sudo systemctl enable checkin-celery-beat
sudo systemctl enable nginx
```

### 7. Start All Services
```bash
sudo systemctl start redis-server
sudo systemctl start checkin-gunicorn
sudo systemctl start checkin-celery
sudo systemctl start checkin-celery-beat
sudo systemctl restart nginx
```

### 8. Verify All Services Running
```bash
sudo systemctl status redis-server
sudo systemctl status checkin-gunicorn
sudo systemctl status checkin-celery
sudo systemctl status checkin-celery-beat
sudo systemctl status nginx
```

---

## What Happens on System Reboot?

When your server reboots, all services will **automatically start** in this order:

1. **Redis** starts first
2. **Gunicorn** starts (depends on Redis)
3. **Celery Worker** starts (depends on Redis)
4. **Celery Beat** starts (depends on Redis and Celery Worker)
5. **Nginx** starts

If any service crashes, systemd will **automatically restart** it.

---

## Service Management Commands

### Check Status
```bash
# All services
sudo systemctl status checkin-gunicorn checkin-celery checkin-celery-beat nginx redis-server

# Individual service
sudo systemctl status checkin-gunicorn
```

### Restart Services
```bash
# Restart application (zero downtime)
sudo systemctl reload checkin-gunicorn

# Restart all
sudo systemctl restart checkin-gunicorn checkin-celery checkin-celery-beat
```

### Stop Services
```bash
sudo systemctl stop checkin-gunicorn checkin-celery checkin-celery-beat
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u checkin-gunicorn -f
sudo journalctl -u checkin-celery -f

# Application logs
sudo tail -f /var/log/checkin/gunicorn-error.log
sudo tail -f /var/log/checkin/celery-worker.log
```

---

## Environment Variables for Production

Update your `.env` file:

```env
# Production mode
DEBUG=False
SECRET_KEY=generate-a-very-long-random-secret-key-here

# Redis for Celery and Channels
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security (when using HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## Testing the Deployment

### 1. Test HTTP API
```bash
curl http://localhost/api/queue/
```

### 2. Test WebSocket
```bash
# Install wscat if needed: npm install -g wscat
wscat -c ws://localhost/ws/queue/
```

### 3. Test Celery (check email task)
Check logs to verify Celery is processing tasks:
```bash
sudo tail -f /var/log/checkin/celery-worker.log
```

### 4. Test Redis
```bash
redis-cli ping
# Should return: PONG
```

---

## Performance Tuning

### Gunicorn Workers
- **Formula**: (2 × CPU cores) + 1
- For 4-core CPU: `--workers 9`

### Celery Workers
- Adjust `--concurrency` based on task type
- I/O bound tasks: More workers
- CPU bound tasks: Match CPU cores

### Redis
Check memory usage:
```bash
redis-cli info memory
```

---

## Monitoring

### Check if all services are active
```bash
sudo systemctl is-active checkin-gunicorn
sudo systemctl is-active checkin-celery
sudo systemctl is-active checkin-celery-beat
sudo systemctl is-active redis-server
sudo systemctl is-active nginx
```

### View resource usage
```bash
# CPU and memory
htop

# Disk usage
df -h

# Redis memory
redis-cli info memory
```

---

## Common Issues

### Celery not processing tasks
```bash
# Check Celery worker is running
sudo systemctl status checkin-celery

# Check Redis connection
redis-cli ping

# View Celery logs
sudo tail -f /var/log/checkin/celery-worker.log
```

### WebSocket not connecting
```bash
# Verify Gunicorn is using Uvicorn workers
sudo journalctl -u checkin-gunicorn | grep -i uvicorn

# Check Nginx WebSocket config
sudo nginx -t
```

### 502 Bad Gateway
```bash
# Check socket file exists
ls -la /home/roni/Desktop/JVAI\ Projects/October/CheckIn/checkin.sock

# Check Gunicorn is running
sudo systemctl status checkin-gunicorn
```

---

## Full Documentation

For complete details, see [deployment.md](deployment.md) which includes:
- SSL/TLS setup with Let's Encrypt
- Database backup procedures
- Update procedures
- Advanced troubleshooting
- Security best practices

---

**Developer**: Roni Ahamed - Backend Developer

*Last Updated: October 29, 2025*
