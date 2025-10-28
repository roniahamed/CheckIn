# Production Deployment Guide

This guide covers deploying the CheckIn application with Nginx, Gunicorn (with Uvicorn workers), and systemd services for automatic startup on system reboot.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Install Dependencies](#install-dependencies)
3. [Create System User](#create-system-user)
4. [Configure Application](#configure-application)
5. [Setup Gunicorn with Uvicorn](#setup-gunicorn-with-uvicorn)
6. [Setup Celery Service](#setup-celery-service)
7. [Setup Celery Beat Service](#setup-celery-beat-service)
8. [Setup Nginx](#setup-nginx)
9. [Enable and Start Services](#enable-and-start-services)
10. [SSL/TLS Configuration](#ssltls-configuration)
11. [Monitoring and Logs](#monitoring-and-logs)

---

## Prerequisites

- Ubuntu/Debian Linux system
- Root or sudo access
- Domain name (optional, for production)
- Python 3.12+
- Redis installed and running

---

## Install Dependencies

### System Packages

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx redis-server supervisor
```

### Python Packages

```bash
# Activate your virtual environment
source /home/roni/Desktop/JVAI\ Projects/October/CheckIn/env/bin/activate

# Install production dependencies
pip install gunicorn uvicorn[standard]
```

---

## Create System User

Create a dedicated user for running the application (recommended for security):

```bash
# Create system user
sudo useradd -r -s /bin/bash -d /home/checkin -m checkin

# Add current user to checkin group (optional)
sudo usermod -a -G checkin $USER

# Set ownership
sudo chown -R checkin:checkin /home/roni/Desktop/JVAI\ Projects/October/CheckIn
```

**Note**: For development/testing, you can skip this and use your current user (roni).

---

## Configure Application

### 1. Update Environment Variables

Edit `.env` file:

```bash
nano /home/roni/Desktop/JVAI\ Projects/October/CheckIn/.env
```

Update for production:

```env
# Production Settings
DEBUG=False
SECRET_KEY=your-secure-production-secret-key-here-min-50-chars

# Allowed Hosts (add your domain)
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Site URLs
SITE_URL=https://your-domain.com
SITE_DOMAIN=https://your-domain.com

# Database (if using PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=checkin_db
DB_USER=checkin_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Media
MEDIA_URL=/media/
MEDIA_ROOT=/home/roni/Desktop/JVAI Projects/October/CheckIn/media
```

### 2. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 3. Run Migrations

```bash
python manage.py migrate
```

---

## Setup Gunicorn with Uvicorn

### 1. Create Gunicorn Configuration File

```bash
sudo nano /etc/systemd/system/checkin-gunicorn.service
```

Add the following content:

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
    --log-level info \
    CheckIn.asgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Create Log Directory

```bash
sudo mkdir -p /var/log/checkin
sudo chown roni:roni /var/log/checkin
```

### 3. Recommended Worker Configuration

Calculate workers based on CPU cores:

```bash
# Formula: (2 x $num_cores) + 1
# For 4 cores: (2 x 4) + 1 = 9 workers
```

Update `--workers` in the service file accordingly.

---

## Setup Celery Service

### 1. Create Celery Worker Service

```bash
sudo nano /etc/systemd/system/checkin-celery.service
```

Add the following:

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

ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Create PID Directory

```bash
sudo mkdir -p /var/run/celery
sudo chown roni:roni /var/run/celery
```

---

## Setup Celery Beat Service

### 1. Create Celery Beat Service

```bash
sudo nano /etc/systemd/system/checkin-celery-beat.service
```

Add the following:

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

ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Setup Nginx

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/checkin
```

Add the following configuration:

```nginx
upstream checkin_app {
    server unix:/home/roni/Desktop/JVAI\ Projects/October/CheckIn/checkin.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    access_log /var/log/nginx/checkin-access.log;
    error_log /var/log/nginx/checkin-error.log;

    location /static/ {
        alias /home/roni/Desktop/JVAI\ Projects/October/CheckIn/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/roni/Desktop/JVAI\ Projects/October/CheckIn/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://checkin_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /ws/ {
        proxy_pass http://checkin_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket timeout
        proxy_read_timeout 86400;
    }
}
```

### 2. Enable Nginx Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/checkin /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default
```

### 3. Adjust Permissions

```bash
# Allow Nginx to access the socket
sudo usermod -a -G roni www-data

# Set permissions on project directory
chmod 755 /home/roni
chmod 755 /home/roni/Desktop
chmod 755 "/home/roni/Desktop/JVAI Projects"
chmod 755 "/home/roni/Desktop/JVAI Projects/October"
chmod 755 "/home/roni/Desktop/JVAI Projects/October/CheckIn"
```

---

## Enable and Start Services

### 1. Reload Systemd

```bash
sudo systemctl daemon-reload
```

### 2. Enable Services (Auto-start on Boot)

```bash
# Enable Redis (if not already enabled)
sudo systemctl enable redis-server

# Enable Gunicorn
sudo systemctl enable checkin-gunicorn

# Enable Celery Worker
sudo systemctl enable checkin-celery

# Enable Celery Beat
sudo systemctl enable checkin-celery-beat

# Enable Nginx
sudo systemctl enable nginx
```

### 3. Start Services

```bash
# Start Redis
sudo systemctl start redis-server

# Start Gunicorn
sudo systemctl start checkin-gunicorn

# Start Celery Worker
sudo systemctl start checkin-celery

# Start Celery Beat
sudo systemctl start checkin-celery-beat

# Restart Nginx
sudo systemctl restart nginx
```

### 4. Check Service Status

```bash
# Check all services
sudo systemctl status checkin-gunicorn
sudo systemctl status checkin-celery
sudo systemctl status checkin-celery-beat
sudo systemctl status nginx
sudo systemctl status redis-server
```

---

## SSL/TLS Configuration

### Using Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

The certbot will automatically update your Nginx configuration for HTTPS.

---

## Monitoring and Logs

### View Logs

```bash
# Gunicorn logs
sudo tail -f /var/log/checkin/gunicorn-access.log
sudo tail -f /var/log/checkin/gunicorn-error.log

# Celery logs
sudo tail -f /var/log/checkin/celery-worker.log
sudo tail -f /var/log/checkin/celery-beat.log

# Nginx logs
sudo tail -f /var/log/nginx/checkin-access.log
sudo tail -f /var/log/nginx/checkin-error.log

# System logs for services
sudo journalctl -u checkin-gunicorn -f
sudo journalctl -u checkin-celery -f
sudo journalctl -u checkin-celery-beat -f
```

### Restart Services

```bash
# Restart individual services
sudo systemctl restart checkin-gunicorn
sudo systemctl restart checkin-celery
sudo systemctl restart checkin-celery-beat
sudo systemctl restart nginx

# Restart all CheckIn services
sudo systemctl restart checkin-gunicorn checkin-celery checkin-celery-beat
```

### Reload Gunicorn (Zero Downtime)

```bash
sudo systemctl reload checkin-gunicorn
```

---

## Common Issues and Solutions

### Issue: Socket file not created

**Solution**:
```bash
# Check Gunicorn service status
sudo systemctl status checkin-gunicorn

# Check logs
sudo journalctl -u checkin-gunicorn -n 50
```

### Issue: Permission denied on socket

**Solution**:
```bash
# Add www-data to your user group
sudo usermod -a -G roni www-data

# Restart Nginx
sudo systemctl restart nginx
```

### Issue: 502 Bad Gateway

**Solution**:
```bash
# Check if Gunicorn is running
sudo systemctl status checkin-gunicorn

# Check socket file exists
ls -la /home/roni/Desktop/JVAI\ Projects/October/CheckIn/checkin.sock

# Check Nginx error logs
sudo tail -f /var/log/nginx/checkin-error.log
```

### Issue: WebSocket not connecting

**Solution**:
```bash
# Ensure Uvicorn workers are being used
sudo systemctl status checkin-gunicorn

# Check WebSocket specific logs
sudo tail -f /var/log/checkin/gunicorn-error.log | grep -i websocket
```

---

## Performance Tuning

### Gunicorn Workers

Adjust based on your server resources:

```bash
# Edit service file
sudo nano /etc/systemd/system/checkin-gunicorn.service

# Update --workers value
# Formula: (2 x CPU_CORES) + 1
# Example for 4 cores: --workers 9
```

### Nginx Optimization

Add to Nginx configuration:

```nginx
# Inside http block in /etc/nginx/nginx.conf
client_body_buffer_size 128k;
client_max_body_size 10M;
keepalive_timeout 65;
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

---

## Backup and Maintenance

### Database Backup (PostgreSQL)

```bash
# Create backup
pg_dump checkin_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql checkin_db < backup_20251029.sql
```

### Media Files Backup

```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz /home/roni/Desktop/JVAI\ Projects/October/CheckIn/media/
```

### Automated Backup Script

Create `/home/roni/backup_checkin.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/roni/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump checkin_db > $BACKUP_DIR/db_$DATE.sql

# Backup media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/roni/Desktop/JVAI\ Projects/October/CheckIn/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add line:
0 2 * * * /home/roni/backup_checkin.sh
```

---

## Testing Production Setup

```bash
# Test application
curl http://localhost/api/queue/

# Test WebSocket
wscat -c ws://localhost/ws/queue/

# Check all services are running
sudo systemctl is-active checkin-gunicorn
sudo systemctl is-active checkin-celery
sudo systemctl is-active checkin-celery-beat
sudo systemctl is-active nginx
sudo systemctl is-active redis-server
```

---

## Updating Application

```bash
# Pull latest code
cd /home/roni/Desktop/JVAI\ Projects/October/CheckIn
git pull

# Activate virtual environment
source env/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart checkin-gunicorn
sudo systemctl restart checkin-celery
sudo systemctl restart checkin-celery-beat
```

---

**Developer**: Roni Ahamed - Backend Developer

*Last Updated: October 29, 2025*
