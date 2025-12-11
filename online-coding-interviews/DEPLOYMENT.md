# Deployment Guide

## Table of Contents
1. [Docker Deployment](#docker-deployment) ⭐ **Recommended**
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## Docker Deployment

**For comprehensive Docker deployment guide, see: [DOCKER.md](DOCKER.md)**

Quick start:
```bash
cd online-coding-interviews
docker-compose up -d
```

Access the application:
- Frontend: http://localhost:5000
- Backend API: http://localhost:8080

---

## Local Development

### Prerequisites
- Python 3.8+
- Git (optional)
- Modern web browser

### Quick Start

1. **Navigate to project directory:**
   ```bash
   cd online-coding-interviews
   ```

2. **Run startup script:**
   ```bash
   # macOS/Linux
   chmod +x start.sh
   ./start.sh

   # Windows
   start.bat
   ```

3. **Access the application:**
   ```
   http://localhost:8000
   ```

4. **Stop the server:**
   ```bash
   Press Ctrl+C in the terminal
   ```

### Manual Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export PORT=8000  # or set PORT=8000 on Windows

# Run server
python app.py
```

## Production Deployment

### Using Gunicorn + Nginx

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Run with Gunicorn
```bash
cd backend
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --timeout 300 app:app
```

#### 3. Nginx Configuration
```nginx
upstream flask_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates
    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/javascript;

    # WebSocket support
    location / {
        proxy_pass http://flask_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files cache
    location /static {
        proxy_pass http://flask_app;
        expires 7d;
    }
}
```

#### 4. SystemD Service (Linux)
```ini
[Unit]
Description=Coding Interviews Platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/coding-interviews
Environment="PATH=/var/www/coding-interviews/backend/venv/bin"
ExecStart=/var/www/coding-interviews/backend/venv/bin/gunicorn \
    --worker-class eventlet \
    -w 1 \
    --bind unix:coding_interviews.sock \
    app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable coding-interviews
sudo systemctl start coding-interviews
sudo systemctl status coding-interviews
```

### Environment Variables for Production

Create `.env` file:
```bash
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///coding_interviews.db
MAX_CONTENT_LENGTH=16777216  # 16MB
SESSION_TIMEOUT=3600  # 1 hour
```

Load in production:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy application
COPY backend/ .
COPY frontend/ ../frontend/

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000')"

# Run application
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./backend:/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
    restart: unless-stopped
```

### 3. Build and Run Docker

```bash
# Build image
docker build -t coding-interviews:latest .

# Run container
docker run -p 5000:5000 coding-interviews:latest

# Or use docker-compose
docker-compose up -d

# View logs
docker logs -f container_id

# Stop container
docker stop container_id
```

## Cloud Platforms

### Heroku Deployment

1. **Install Heroku CLI:**
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Create Procfile:**
   ```
   web: cd backend && gunicorn --worker-class eventlet -w 1 app:app
   ```

3. **Initialize Heroku:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **View logs:**
   ```bash
   heroku logs --tail
   ```

### AWS Elastic Beanstalk

1. **Install AWS EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize:**
   ```bash
   eb init -p python-3.9 coding-interviews
   ```

3. **Create environment:**
   ```bash
   eb create coding-interviews-prod
   ```

4. **Deploy:**
   ```bash
   eb deploy
   ```

5. **Monitor:**
   ```bash
   eb status
   eb health
   ```

### Digital Ocean App Platform

1. **Connect GitHub repository**
2. **Configure build command:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Configure run command:**
   ```bash
   cd backend && gunicorn --worker-class eventlet -w 1 app:app
   ```
4. **Set environment variables** in dashboard
5. **Deploy**

### Google Cloud Run

1. **Ensure Docker is built**

2. **Push to Google Container Registry:**
   ```bash
   gcloud auth configure-docker
   docker tag coding-interviews:latest gcr.io/PROJECT_ID/coding-interviews
   docker push gcr.io/PROJECT_ID/coding-interviews
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy coding-interviews \
     --image gcr.io/PROJECT_ID/coding-interviews \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Monitoring & Maintenance

### Logging

Set up logging in production (app.py):
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=10)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
```

### Database Backup

```bash
# Backup SQLite database
cp backend/coding_interviews.db backend/coding_interviews.db.backup

# Automated backup (cron job)
0 2 * * * cp /var/www/coding-interviews/backend/coding_interviews.db /backups/coding_interviews_$(date +\%Y\%m\%d).db
```

### Performance Monitoring

Key metrics to track:
- **Response time**: Average API response time
- **WebSocket connections**: Active concurrent connections
- **Server CPU/Memory**: Resource utilization
- **Database query time**: Slow query identification
- **Error rate**: Application errors per minute

Monitor with:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for logging
- **New Relic** or **DataDog** for APM
- **Sentry** for error tracking

### Health Check Endpoint

Add to app.py:
```python
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
```

Use in load balancer health checks.

### Updates & Patches

```bash
# Update dependencies
pip list --outdated
pip install --upgrade package_name

# Test in staging
./start.sh  # Test locally first

# Deploy to production
git push production main
```

### Database Maintenance

```bash
# Vacuum database (optimize)
sqlite3 backend/coding_interviews.db "VACUUM;"

# Analyze for query optimization
sqlite3 backend/coding_interviews.db "ANALYZE;"

# Check database integrity
sqlite3 backend/coding_interviews.db "PRAGMA integrity_check;"
```

### Disaster Recovery

1. **Regular backups** (daily)
2. **Test restore procedure** (weekly)
3. **Document recovery steps**
4. **Keep backups in multiple locations** (local + cloud)
5. **Version control** for code recovery

## Performance Tuning

### Application Level
- Enable Gzip compression
- Use CDN for static assets
- Implement caching
- Optimize database queries

### Database Level
- Add indexes on frequently queried columns
- Archive old sessions
- Use connection pooling

### Server Level
- Increase Gunicorn workers
- Enable HTTP keep-alive
- Use WebSocket compression
- Implement rate limiting

### Network Level
- Use CDN
- Enable HTTP/2
- Implement caching headers
- Use compression

## Troubleshooting Production Issues

### High Memory Usage
```bash
# Monitor memory
top -p $(pgrep -f gunicorn)

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### WebSocket Disconnections
- Check firewall rules
- Verify proxy supports WebSocket
- Increase timeout values
- Monitor network stability

### Database Locks
- Check for long-running queries
- Optimize slow queries
- Use WAL mode: `PRAGMA journal_mode=WAL;`
- Increase cache_size

### Slow Responses
- Profile with `cProfile`
- Analyze slow queries with `EXPLAIN PLAN`
- Cache frequently accessed data
- Scale horizontally with load balancer

---

**Ready to Deploy! 🚀**
