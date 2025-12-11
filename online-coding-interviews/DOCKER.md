# Docker Deployment Guide

> **Quick Start**: `docker-compose up -d` then visit http://localhost:8080

## Table of Contents
1. [Quick Start (5 minutes)](#quick-start)
2. [What's Included](#whats-included)
3. [Docker Architecture](#docker-architecture)
4. [Commands Reference](#commands-reference)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

## Overview
The application is containerized in a single Docker image containing both the Flask backend and static frontend.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **WebSocket**: ws://localhost:5000/socket.io/

### Option 2: Using Docker Directly

```bash
# Build the image
docker build -t coding-interview-platform .

# Run the container
docker run -d \
  --name coding-interview-platform \
  -p 5000:5000 \
  -p 8080:8080 \
  -v $(pwd)/backend/instance:/app/backend/instance \
  coding-interview-platform

# View logs
docker logs -f coding-interview-platform

# Stop the container
docker stop coding-interview-platform
```

## Image Details

- **Base Image**: `python:3.9-slim`
- **Backend Port**: 5000 (Flask with SocketIO)
- **Frontend Port**: 8080 (Python HTTP server)
- **Volume**: `/app/backend/instance` (for SQLite database persistence)

## What's Included

✅ **Single Container** - Backend (Flask/SocketIO) + Frontend (Static files)
✅ **Multi-Stage Build** - Optimized image (~350-400MB)
✅ **Data Persistence** - SQLite database survives container restarts
✅ **Health Checks** - Automatic container health monitoring
✅ **Docker Compose** - One-command deployment
✅ **Zero Configuration** - Works out of the box

## Docker Architecture

```
┌─────────────────────────────────────────┐
│  Docker Container (python:3.9-slim)    │
├─────────────────────────────────────────┤
│ Backend                 │ Frontend       │
│ (Flask/SocketIO)       │ (Static files) │
│ Port 5000              │ Port 8080      │
│ • REST API             │ • HTML/CSS/JS  │
│ • WebSocket            │ • Ace Editor   │
│ • Session mgmt         │ • Pyodide      │
├─────────────────────────────────────────┤
│  SQLite Database (Persistent Volume)    │
└─────────────────────────────────────────┘
```

## Commands Reference

### Start & Stop
```bash
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose restart            # Restart
docker-compose logs -f            # View logs
docker-compose ps                 # Status
```

### Testing
```bash
docker-compose exec app python -m pytest backend/ -v           # All tests
docker-compose exec app python -m pytest backend/test_unit.py -v  # Unit tests
docker-compose exec app python -m pytest backend/test_integration.py -v  # Integration
```

### Container Management
```bash
docker-compose exec app /bin/bash          # Enter container
docker-compose exec app curl http://localhost:5000/health  # Health check
docker-compose exec app ls -la backend/instance  # Check database
```

### Database Management
```bash
docker-compose exec app rm /app/backend/instance/coding_interviews.db  # Reset DB
docker-compose exec app sqlite3 /app/backend/instance/coding_interviews.db ".tables"  # Query DB
```

## Environment Variables

- `FLASK_ENV`: Set to `production` (can override to `development`)
- `PYTHONUNBUFFERED`: Set to `1` (ensures Python output is sent to logs)
- `FLASK_APP`: Set to `backend/app.py`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Container won't start** | `docker-compose logs -f` to see errors |
| **Port 5000/8080 already in use** | Edit docker-compose.yml: `5001:5000` or `8081:8080` |
| **Database errors** | `docker-compose exec app rm /app/backend/instance/coding_interviews.db` |
| **Can't connect to database** | Restart container: `docker-compose restart` |
| **Health check failing** | Check logs: `docker-compose logs -f` |
| **Want to reset everything** | `docker-compose down -v` (removes volumes) |

## Building and Optimization

The Dockerfile uses a multi-stage build to reduce image size:
1. **Stage 1 (Builder)**: Installs Python dependencies
2. **Stage 2 (Final)**: Contains only runtime dependencies and application code

Result: ~350-400MB image size

## Accessing the Application

### From localhost:
- Frontend: http://localhost:8080
- Create Session: http://localhost:8080 (fill form to create)

### From Docker Desktop:
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000

### From other machines on the network:
Replace `localhost` with your machine's IP address, e.g., `http://192.168.1.100:8080`

## Troubleshooting
## Production Deployment

For production deployment considerations, see [DEPLOYMENT.md](DEPLOYMENT.md)

Key points for production:
- Use a production WSGI server (Gunicorn, uWSGI)
- Add a reverse proxy (Nginx) for static files
- Enable HTTPS/SSL
- Use environment variables for secrets
- Set up proper logging and monitoring
- Consider managed databases (PostgreSQL, MySQL)
- Implement health checks and auto-recovery

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
